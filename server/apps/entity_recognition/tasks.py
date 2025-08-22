# apps/entity_recognition/tasks.py
from celery import shared_task
from pymongo import MongoClient
from django.conf import settings
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import logging
from .services.sports_entity_detector import SportsEntityDetector
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class NERProcessor:
    def __init__(self, model_path='models/fine_tuned_arabert_ner'):
        try:
            # Resolve model path
            base_dir = Path(__file__).resolve().parent.parent.parent
            abs_model_path = base_dir / model_path
            fallback_model = "CAMeL-Lab/bert-base-arabic-camelbert-msa-ner"

            if not abs_model_path.exists():
                logger.warning(f"Model path {abs_model_path} does not exist, using fallback: {fallback_model}")
                abs_model_path = fallback_model
            else:
                abs_model_path = str(abs_model_path)

            # Load Transformers model
            self.model = AutoModelForTokenClassification.from_pretrained(abs_model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(abs_model_path)
            self.ner_pipeline = pipeline(
                'ner',
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=0 if os.environ.get('CUDA_AVAILABLE') else -1
            )

            # Initialize sports detector with camel-tools model
            camel_model_path = str(base_dir / 'models/camelbert_ner')
            self.sports_detector = SportsEntityDetector(camel_model_path)
            logger.info(f"NER processor initialized with Transformers model: {abs_model_path}, Camel model: {camel_model_path}")
        except Exception as e:
            logger.error(f"Error initializing NER processor: {str(e)}")
            raise

    def process_text(self, text):
        """Process text with both Transformers and SportsEntityDetector, combining results."""
        if not text or text.strip() == '':
            logger.warning("Empty text provided for NER processing")
            return []

        try:
            # Truncate text if too long
            tokens = self.tokenizer(text, truncation=False, return_tensors='pt')
            token_count = tokens['input_ids'].shape[1]
            if token_count > 512:
                logger.info(f"Truncating text from {token_count} tokens")
                text = self.tokenizer.decode(
                    self.tokenizer(text, truncation=True, max_length=512)['input_ids'],
                    skip_special_tokens=True
                )

            # Transformers pipeline
            transformer_results = self.ner_pipeline(text)
            transformer_entities = []
            for r in transformer_results:
                label = r['entity_group']
                mapped_label = (
                    'PLAYER' if label.endswith('PER') or label == 'B-PER' or label == 'I-PER' else
                    'TEAM' if label.endswith('ORG') or label == 'B-ORG' or label == 'I-ORG' else
                    'COMPETITION' if label.endswith('LOC') or label == 'B-LOC' or label == 'I-LOC' else
                    'UNKNOWN'
                )
                if mapped_label != 'UNKNOWN':
                    transformer_entities.append({
                        'text': r['word'],
                        'label': mapped_label
                    })

            logger.debug(f"Transformer entities: {transformer_entities}")

            # Sports detector
            sports_entities = self.sports_detector.detect_entities(text)
            logger.debug(f"Sports detector entities: {sports_entities}")

            # Merge results
            seen_texts = set()
            final_entities = []

            # Prioritize sports detector (more sports-specific)
            for entity in sports_entities:
                if entity['text'] not in seen_texts:
                    final_entities.append(entity)
                    seen_texts.add(entity['text'])

            # Add transformer entities if not already included
            for entity in transformer_entities:
                if entity['text'] not in seen_texts:
                    final_entities.append(entity)
                    seen_texts.add(entity['text'])

            logger.info(f"Final entities: {final_entities}")
            return final_entities
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return []

@shared_task
def apply_ner_to_processed_data(processed_data_id=None):
    """
    Apply NER to processed data. If ID is provided, process one document;
    otherwise, process all unanalyzed documents.
    """
    try:
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        processor = NERProcessor()
        
        if processed_data_id:
            comment = db['text_processing_processeddata'].find_one({'_id': processed_data_id})
            if not comment:
                logger.error(f"Document with ID {processed_data_id} not found")
                return False
                
            if comment.get('is_analyzed_for_entities', False):
                logger.info(f"Document ID {processed_data_id} already analyzed")
                return True
                
            entities = processor.process_text(comment['normalized_text'])
            result = db['text_processing_processeddata'].update_one(
                {'_id': processed_data_id},
                {'$set': {
                    'entities': entities,
                    'is_analyzed_for_entities': True
                }}
            )
            if result.modified_count == 0:
                logger.warning(f"No update for document ID {processed_data_id}")
            logger.info(f"Applied NER to document ID: {processed_data_id}, entities: {entities}")
            return True
        else:
            comments = db['text_processing_processeddata'].find({'is_analyzed_for_entities': {'$ne': True}})
            count = 0
            failed_count = 0
            
            for comment in comments:
                try:
                    entities = processor.process_text(comment['normalized_text'])
                    result = db['text_processing_processeddata'].update_one(
                        {'_id': comment['_id']},
                        {'$set': {
                            'entities': entities,
                            'is_analyzed_for_entities': True
                        }}
                    )
                    if result.modified_count == 0:
                        logger.warning(f"No update for document ID {comment['_id']}")
                    logger.info(f"Applied NER to document ID: {comment['_id']}, entities: {entities}")
                    count += 1
                except Exception as e:
                    logger.error(f"Error processing document {comment['_id']}: {str(e)}")
                    db['text_processing_processeddata'].update_one(
                        {'_id': comment['_id']},
                        {'$set': {'is_analyzed_for_entities': True, 'entities': []}}
                    )
                    failed_count += 1
            
            client.close()
            summary = f"Applied NER to {count} documents, {failed_count} failed"
            logger.info(summary)
            return summary
    except Exception as e:
        logger.error(f"Error in apply_ner_to_processed_data: {str(e)}", exc_info=True)
        raise

@shared_task
def apply_ner_to_all_unanalyzed():
    """Wrapper task to process all unanalyzed documents."""
    return apply_ner_to_processed_data()