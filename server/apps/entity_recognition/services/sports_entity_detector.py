# apps/entity_recognition/services/sports_entity_detector.py
import re
import logging
from camel_tools.ner import NERecognizer
from camel_tools.tokenizers.word import simple_word_tokenize
from django.conf import settings

logger = logging.getLogger(__name__)

class SportsEntityDetector:
    def __init__(self, model_path='models/camelbert_ner'):
        """
        Initialize the Sports Entity Detector with both rule-based and model-based components.
        
        Args:
            model_path: Path to the saved CamelBERT NER model
        """
        self.model_path = model_path
        try:
            self.ner = NERecognizer(model_path)
            logger.info(f"SportsEntityDetector initialized with model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to initialize NERecognizer with {model_path}: {str(e)}")
            raise

        # Expanded sports lexicon
        self.lexicon = {
            'players': [
                'محمد صلاح', 'ليونيل ميسي', 'كريستيانو رونالدو', 'كريم بنزيما', 'نيمار',
                'كيليان مبابي', 'روبرت ليفاندوفسكي', 'هاري كين', 'إرلينغ هالاند',
                'زين الدين زيدان', 'رونالدينيو', 'ديفيد بيكهام', 'أحمد حسن', 'سامي الجابر',
                'رياض محرز', 'ساديو ماني', 'فيرجيل فان دايك', 'كيفن دي بروين'
            ],
            'teams': [
                'نادي الهلال', 'نادي النصر', 'نادي الأهلي', 'ريال مدريد', 'برشلونة',
                'منتخب مصر', 'منتخب السعودية', 'منتخب الكويت', 'مانشستر يونايتد',
                'ليفربول', 'يوفنتوس', 'بايرن ميونخ', 'باريس سان جيرمان', 'تشيلسي',
                'مانشستر سيتي', 'أرسنال', 'إنتر ميلان', 'ميلان'
            ],
            'competitions': [
                'كأس العالم', 'دوري أبطال أوروبا', 'الدوري الإسباني', 'الدوري الإنجليزي',
                'الدوري السعودي', 'كأس أمم إفريقيا', 'كأس آسيا', 'أولمبياد',
                'كأس الخليج', 'كأس السوبر الإسباني', 'كأس العالم للأندية', 'ويمبلدون',
                'دوري أبطال آسيا', 'كأس السوبر السعودي'
            ]
        }

        self.patterns = {
            'player': [
                r'[ء-ي]{2,}\s+[ء-ي]{2,}(?:\s+[ء-ي]{2,})?',  # Full name
                r'(?:الملك|الأسطورة|نجم|هداف)\s+[ء-ي]{2,}',  # Nickname
                r'(?:لاعب|نجم|هداف)\s+[ء-ي]{2,}'  # Single name in context
            ],
            'team': [
                r'(?:نادي|فريق)\s+[ء-ي]{2,}(?:\s+[ء-ي]{2,})?',
                r'منتخب\s+[ء-ي]{2,}',
                r'(?:ريال\s+مدريد|برشلونة|الهلال|الأهلي|ليفربول|مانشستر\s+[ء-ي]+)',
                r'[ء-ي]{2,}\s*(?:FC|Club)'
            ],
            'competition': [
                r'(?:كأس|دوري|بطولة)\s+[ء-ي]{2,}(?:\s+[ء-ي]{2,})?',
                r'(?:أولمبياد|بطولة)\s*(?:[ء-ي]{2,}|\d{4})',
                r'كأس\s+العالم(?:\s*\d{4})?'
            ]
        }

        self.context_keywords = {
            'player': ['لاعب', 'نجم', 'هداف', 'موهبة', 'هدف', 'تمريرة', 'مهاجم', 'مدافع'],
            'team': ['فريق', 'نادي', 'منتخب', 'مباراة', 'يفوز', 'يواجه', 'تشكيلة'],
            'competition': ['بطولة', 'كأس', 'دوري', 'نهائي', 'افتتاحية', 'تصفيات']
        }

    def rule_based_detection(self, text):
        """Apply rule-based pattern matching to detect entities."""
        entities = {'PLAYER': [], 'TEAM': [], 'COMPETITION': []}
        tokens = simple_word_tokenize(text)

        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.UNICODE)
                for match in matches:
                    entity_text = match.group().strip()
                    if self._has_context(entity_text, tokens, entity_type):
                        entities[entity_type.upper()].append(entity_text)

        for entity_type, entity_list in self.lexicon.items():
            entity_key = entity_type.upper()[:-1] if entity_type.endswith('s') else entity_type.upper()
            for entity in entity_list:
                if entity in text:
                    entities[entity_key].append(entity)

        for entity_type in entities:
            entities[entity_type] = list(dict.fromkeys(entities[entity_type]))

        logger.debug(f"Rule-based detection: {entities}")
        return entities

    def _has_context(self, entity, tokens, entity_type):
        """Check if entity has relevant context keywords nearby."""
        context_window = 5
        entity_tokens = simple_word_tokenize(entity)
        start_idx = next((i for i, t in enumerate(tokens) if t == entity_tokens[0]), -1)
        if start_idx == -1:
            return False

        window = tokens[max(0, start_idx - context_window):start_idx + len(entity_tokens) + context_window]
        return any(keyword in window for keyword in self.context_keywords[entity_type])

    def model_based_detection(self, tokens):
        """Apply camel-tools NER to detect entities."""
        entities = {'PLAYER': [], 'TEAM': [], 'COMPETITION': []}
        try:
            ner_labels = self.ner.predict_sentence(tokens)
        except Exception as e:
            logger.error(f"Error in camel-tools NER: {str(e)}")
            return entities

        current_entity = []
        current_label = None
        for token, label in zip(tokens, ner_labels):
            if label.startswith('B-'):
                if current_entity:
                    entity_text = ' '.join(current_entity)
                    if current_label == 'PER':
                        entities['PLAYER'].append(entity_text)
                    elif current_label == 'ORG':
                        entities['TEAM'].append(entity_text)
                    elif current_label == 'LOC' and entity_text in self.lexicon['competitions']:
                        entities['COMPETITION'].append(entity_text)
                current_entity = [token]
                current_label = label[2:]
            elif label.startswith('I-') and current_label == label[2:]:
                current_entity.append(token)
            else:
                if current_entity:
                    entity_text = ' '.join(current_entity)
                    if current_label == 'PER':
                        entities['PLAYER'].append(entity_text)
                    elif current_label == 'ORG':
                        entities['TEAM'].append(entity_text)
                    elif current_label == 'LOC' and entity_text in self.lexicon['competitions']:
                        entities['COMPETITION'].append(entity_text)
                current_entity = []
                current_label = None

        if current_entity:
            entity_text = ' '.join(current_entity)
            if current_label == 'PER':
                entities['PLAYER'].append(entity_text)
            elif current_label == 'ORG':
                entities['TEAM'].append(entity_text)
            elif current_label == 'LOC' and entity_text in self.lexicon['competitions']:
                entities['COMPETITION'].append(entity_text)

        logger.debug(f"Model-based detection: {entities}")
        return entities

    def detect_entities(self, text):
        """Hybrid detection: Combine rule-based and model-based NER."""
        if not text or text.strip() == '':
            logger.warning("Empty text provided for entity detection")
            return []

        tokens = simple_word_tokenize(text)
        rule_entities = self.rule_based_detection(text)
        model_entities = self.model_based_detection(tokens)

        combined = {'PLAYER': [], 'TEAM': [], 'COMPETITION': []}
        for entity_type in combined:
            combined[entity_type] = list(dict.fromkeys(model_entities[entity_type]))
            for entity in rule_entities[entity_type]:
                if entity not in combined[entity_type]:
                    combined[entity_type].append(entity)

        formatted_entities = []
        for entity_type, entities in combined.items():
            for entity in entities:
                formatted_entities.append({
                    'text': entity,
                    'label': entity_type
                })

        logger.info(f"Detected entities: {formatted_entities}")
        return formatted_entities