# apps/sentiment_analysis/tasks.py
from celery import shared_task
from pymongo import MongoClient
from django.conf import settings
import logging
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os
from transformers import pipeline, __version__ as transformers_version
import time

logger = logging.getLogger(__name__)

# Singleton for SentimentAnalyzer
_sentiment_analyzer = None

def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        logger.info("Initializing fine-tuned sentiment analysis model")
        model_path = os.path.join(settings.BASE_DIR, 'models', 'fine_tuned_arabert_v2')
        if not os.path.exists(model_path):
            logger.error(f"Model path {model_path} does not exist")
            raise FileNotFoundError(f"Model path {model_path} does not exist")
        try:
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            _sentiment_analyzer = (model, tokenizer)
            logger.info(f"Fine-tuned sentiment analysis model initialized (transformers version: {transformers_version})")
        except Exception as e:
            logger.error(f"Error loading fine-tuned model: {str(e)}")
            raise
    return _sentiment_analyzer

@shared_task
def apply_sentiment_to_all_unanalyzed():
    """Apply sentiment analysis to unanalyzed comments in text_processing_processeddata."""
    start_time = time.time()
    try:
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        collection = db['text_processing_processeddata']
        
        # Initialize pipeline with truncation and top_k
        model, tokenizer = get_sentiment_analyzer()
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            truncation=True,
            max_length=512,
            top_k=None,  # Replaced return_all_scores=True
            device=0 if os.environ.get('CUDA_AVAILABLE') else -1  # Use GPU if available
        )

        # Fetch unanalyzed comments
        cursor = collection.find({'is_analyzed_for_sentiment': {'$ne': True}}).batch_size(100)
        count = 0
        failed_count = 0
        batch = []
        batch_ids = []
        batch_raw_ids = []
        batch_size = 100
        sentiment_map = {'LABEL_0': 'negative', 'LABEL_1': 'positive', 'LABEL_2': 'neutral'}

        for data in cursor:
            doc_id = data['_id']
            raw_data_id = data.get('raw_data', '')
            text = data.get('normalized_text', '')

            # Validate input
            if not text or text.strip() == '':
                logger.warning(f"Skipping comment ID {raw_data_id}: Empty text")
                collection.update_one(
                    {'_id': doc_id},
                    {'$set': {'is_analyzed_for_sentiment': True, 'sentiment': {'label': 'SKIPPED', 'text': 'skipped', 'score': 0.0}}}
                )
                failed_count += 1
                continue

            # Check token count
            tokens = tokenizer(text, truncation=False, return_tensors='pt')
            token_count = tokens['input_ids'].shape[1]
            if token_count > 512:
                logger.info(f"Comment ID {raw_data_id} will be truncated from {token_count} tokens")

            batch.append(text)
            batch_ids.append(doc_id)
            batch_raw_ids.append(raw_data_id)

            if len(batch) >= batch_size:
                try:
                    sentiments = sentiment_pipeline(batch)
                    for _id, raw_id, sentiment in zip(batch_ids, batch_raw_ids, sentiments):
                        sentiment_label = max(sentiment, key=lambda x: x['score'])['label']
                        sentiment_text = sentiment_map.get(sentiment_label, 'unknown')
                        sentiment_score = max(s['score'] for s in sentiment)

                        # Validate scores
                        total_score = sum(s['score'] for s in sentiment)
                        if not 0.99 <= total_score <= 1.01:
                            logger.warning(f"Comment ID {raw_id}: Invalid score sum {total_score}")

                        logger.info(f"Processed comment ID {raw_id}: label={sentiment_label}, text={sentiment_text}, score={sentiment_score}")

                        collection.update_one(
                            {'_id': _id},
                            {
                                '$set': {
                                    'sentiment': {
                                        'label': sentiment_label,
                                        'text': sentiment_text,
                                        'score': sentiment_score
                                    },
                                    'is_analyzed_for_sentiment': True
                                }
                            }
                        )
                        count += 1
                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
                    for _id, raw_id in zip(batch_ids, batch_raw_ids):
                        collection.update_one(
                            {'_id': _id},
                            {'$set': {'is_analyzed_for_sentiment': True, 'sentiment': {'label': 'ERROR', 'text': 'error', 'score': 0.0}}}
                        )
                        logger.error(f"Marked comment ID {raw_id} as ERROR: {str(e)}")
                        failed_count += 1
                batch = []
                batch_ids = []
                batch_raw_ids = []

        # Process remaining batch
        if batch:
            try:
                sentiments = sentiment_pipeline(batch)
                for _id, raw_id, sentiment in zip(batch_ids, batch_raw_ids, sentiments):
                    sentiment_label = max(sentiment, key=lambda x: x['score'])['label']
                    sentiment_text = sentiment_map.get(sentiment_label, 'unknown')
                    sentiment_score = max(s['score'] for s in sentiment)

                    # Validate scores
                    total_score = sum(s['score'] for s in sentiment)
                    if not 0.99 <= total_score <= 1.01:
                        logger.warning(f"Comment ID {raw_id}: Invalid score sum {total_score}")

                    logger.info(f"Processed comment ID {raw_id}: label={sentiment_label}, text={sentiment_text}, score={sentiment_score}")

                    collection.update_one(
                        {'_id': _id},
                        {
                            '$set': {
                                'sentiment': {
                                    'label': sentiment_label,
                                    'text': sentiment_text,
                                    'score': sentiment_score
                                },
                                'is_analyzed_for_sentiment': True
                            }
                        }
                    )
                    count += 1
            except Exception as e:
                logger.error(f"Error processing final batch: {str(e)}")
                for _id, raw_id in zip(batch_ids, batch_raw_ids):
                    collection.update_one(
                        {'_id': _id},
                        {'$set': {'is_analyzed_for_sentiment': True, 'sentiment': {'label': 'ERROR', 'text': 'error', 'score': 0.0}}}
                    )
                    logger.error(f"Marked comment ID {raw_id} as ERROR: {str(e)}")
                    failed_count += 1

        client.close()
        duration = time.time() - start_time
        summary = f"Sentiment analysis completed: {count} processed, {failed_count} failed in {duration:.2f} seconds"
        logger.info(summary)
        return summary

    except Exception as e:
        logger.error(f"Sentiment analysis task failed: {str(e)}", exc_info=True)
        raise