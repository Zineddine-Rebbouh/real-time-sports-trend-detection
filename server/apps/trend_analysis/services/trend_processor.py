# apps/trend_analysis/services/trend_processor.py
from collections import Counter
import logging
from django.utils import timezone
from django.conf import settings
from pymongo import MongoClient
from datetime import timedelta, datetime
from camel_tools.utils.normalize import normalize_alef_ar, normalize_teh_marbuta_ar
from camel_tools.tokenizers.word import simple_word_tokenize

logger = logging.getLogger(__name__)

class TrendProcessor:
    def __init__(self, time_window_days=1, entity_types=None, batch_size=1000):
        self.time_window = timedelta(days=time_window_days)
        self.entity_types = entity_types or ['PLAYER', 'TEAM', 'COMPETITION']
        self.batch_size = batch_size
        self.client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        self.db = self.client[settings.DATABASES['default']['NAME']]
        self.sports_lexicon = {
            'keywords': ['كرة القدم', 'كرة السلة', 'تنس', 'ملاكمة', 'كرة الطائرة'],
            'players': ['محمد صلاح', 'كريم بنزيما', 'ليونيل ميسي'],
            'teams': ['الهلال', 'ريال مدريد', 'منتخب مصر'],
            'competitions': ['كأس العالم', 'دوري أبطال أوروبا']
        }

    def normalize_hashtag(self, hashtag):
        """Normalize hashtags for consistency."""
        hashtag = normalize_alef_ar(hashtag)
        hashtag = normalize_teh_marbuta_ar(hashtag)
        hashtag = hashtag.replace('_', '')  # Remove underscores
        return hashtag.lower()

    def detect_topics(self):
        """Detect topics based on hashtags and entities."""
        start_time = timezone.now() - self.time_window
        topics = []

        # Fetch processed data in batches
        cursor = self.db['text_processing_processeddata'].find({
            'processed_at': {'$gte': start_time},
            'is_analyzed_for_entities': True,
            'is_analyzed_for_sentiment': True
        }).batch_size(self.batch_size)

        hashtag_counts = Counter()
        entity_counts = Counter()

        for doc in cursor:
            # Aggregate normalized hashtags
            hashtags = doc.get('hashtags', [])
            for hashtag in hashtags:
                normalized = self.normalize_hashtag(hashtag)
                hashtag_counts[normalized] += 1

            # Aggregate entities
            entities = doc.get('entities', [])
            for entity in entities:
                if entity['label'] in self.entity_types:
                    entity_counts[entity['text']] += 1

        # Create topics from top hashtags
        for hashtag, count in hashtag_counts.most_common(5):
            if count > 10:  # Minimum threshold
                self.db['trend_analysis_topic'].update_one(
                    {'name': hashtag},
                    {
                        '$set': {
                            'count': count,
                            'last_updated': timezone.now(),
                            'keywords': [hashtag],
                            'description': f"Discussion around {hashtag}",
                            'main_entities': self.get_related_entities(hashtag)
                        },
                        '$setOnInsert': {'creation_date': timezone.now()}
                    },
                    upsert=True
                )

        # Create topics from top entities
        for entity, count in entity_counts.most_common(5):
            if count > 10:
                self.db['trend_analysis_topic'].update_one(
                    {'name': entity},
                    {
                        '$set': {
                            'count': count,
                            'last_updated': timezone.now(),
                            'keywords': [entity],
                            'description': f"Discussion around {entity}",
                            'main_entities': [{'text': entity, 'label': next(e['label'] for e in entities if e['text'] == entity)}]
                        },
                        '$setOnInsert': {'creation_date': timezone.now()}
                    },
                    upsert=True
                )

        topics = list(self.db['trend_analysis_topic'].find({'last_updated': {'$gte': start_time}}))
        return topics

    def get_related_entities(self, topic_name):
        """Get entities related to a topic."""
        cursor = self.db['text_processing_processeddata'].find({
            '$or': [
                {'hashtags': {'$in': [topic_name, topic_name.replace('', '_')]}},
                {'entities.text': topic_name}
            ],
            'processed_at': {'$gte': timezone.now() - self.time_window}
        }).limit(5)
        entities = []
        for doc in cursor:
            for entity in doc.get('entities', []):
                if entity['label'] in self.entity_types and entity['text'] != topic_name:
                    entities.append({'text': entity['text'], 'label': entity['label']})
        return entities[:5]

    def analyze_trends(self, topic):
        """Analyze trends for a given topic."""
        start_time = timezone.now() - self.time_window
        query = {
            'processed_at': {'$gte': start_time},
            '$or': [
                {'hashtags': {'$in': [topic['name'], topic['name'].replace('', '_')]}},
                {'entities.text': topic['name']}
            ]
        }
        cursor = self.db['text_processing_processeddata'].find(query).batch_size(self.batch_size)

        # Calculate metrics
        comment_count = 0
        sentiment_dist = {'positive': 0, 'neutral': 0, 'negative': 0}
        influential = []
        sample_comments = []

        for doc in cursor:
            comment_count += 1
            sentiment = doc.get('sentiment')
            if sentiment in ['POSITIVE', 'VERY_POSITIVE']:
                sentiment_dist['positive'] += 1
            elif sentiment == 'NEUTRAL':
                sentiment_dist['neutral'] += 1
            elif sentiment in ['NEGATIVE', 'VERY_NEGATIVE']:
                sentiment_dist['negative'] += 1

            likes = doc.get('likes', 0)
            if likes > 10:
                influential.append(doc['raw_data'])
            if len(sample_comments) < 5:
                sample_comments.append(doc['_id'])

        # Calculate growth rate
        prev_window = start_time - self.time_window
        prev_count = self.db['text_processing_processeddata'].count_documents({
            'processed_at': {'$gte': prev_window, '$lt': start_time},
            '$or': [{'hashtags': {'$in': [topic['name'], topic['name'].replace('', '_')]}}, {'entities.text': topic['name']}]
        })
        growth_rate = ((comment_count - prev_count) / (prev_count + 1)) * 100

        # Determine trend status
        status = 'emerging' if comment_count < 50 or growth_rate > 20 else 'peaking' if comment_count < 200 else 'declining'

        # Save trend
        trend = self.db['trend_analysis_trend'].update_one(
            {'topic_name': topic['name']},
            {
                '$set': {
                    'name': f"{topic['name']} Trend",
                    'description': f"Trend related to {topic['name']}",
                    'trend_metrics': {'comment_count': comment_count, 'growth_rate': growth_rate},
                    'sentiment_distribution': sentiment_dist,
                    'influential_sources': influential[:3],
                    'status': status,
                    'last_updated': timezone.now(),
                    'sample_content': sample_comments
                },
                '$setOnInsert': {'detection_time': timezone.now()}
            },
            upsert=True
        )

        # Save analytics result
        self.db['trend_analysis_analyticsresult'].insert_one({
            'analysis_type': 'volume',
            'time_period_start': start_time,
            'time_period_end': timezone.now(),
            'data_points': {'comment_count': comment_count},
            'insights': [f"Trend {topic['name']} has {comment_count} comments"],
            'related_trends': [topic['name']],
            'metadata': {'topic': topic['name']},
            'created_at': timezone.now(),
            'analysis_version': 'v1'
        })

        return topic['name']

    def process_trends(self):
        """Process all trends and save analytics."""
        topics = self.detect_topics()
        trends = []

        for topic in topics:
            trend = self.analyze_trends(topic)
            trends.append(trend)

        return {
            'trend_count': len(trends),
            'topics': [t['name'] for t in topics]
        }

    def __del__(self):
        """Close MongoDB connection."""
        self.client.close()