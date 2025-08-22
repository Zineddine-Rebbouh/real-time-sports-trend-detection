# apps/trend_analysis/tasks.py
from celery import shared_task
from pymongo import MongoClient
from django.conf import settings
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from camel_tools.tokenizers.word import simple_word_tokenize
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

@shared_task
def analyze_trends(time_window_days=7, entity_types=['PLAYER', 'TEAM', 'COMPETITION']):
    """Analyze trends and compute all dashboard data, including author name in sample comments."""
    try:
        start_time = datetime.utcnow()
        logger.info(f"Starting trend analysis: time_window_days={time_window_days}, entity_types={entity_types}")

        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        processed_collection = db['text_processing_processeddata']
        rawdata_collection = db['data_collection_rawdata']

        # Log database info
        logger.info(f"Connected to database: {settings.DATABASES['default']['NAME']}")
        total_docs = processed_collection.count_documents({})
        logger.info(f"Total documents in text_processing_processeddata: {total_docs}")

        # Sentiment mapping
        sentiment_map = {
            'LABEL_0': 'negative',
            'LABEL_1': 'positive',
            'LABEL_2': 'neutral'
        }

        # Calculate time window
        cutoff = start_time - timedelta(days=time_window_days)
        logger.info(f"Time window: processed_at >= {cutoff}")

        # Log documents in time window
        time_window_docs = processed_collection.count_documents({'processed_at': {'$gte': cutoff}})
        logger.info(f"Documents in time window: {time_window_docs}")

        # Log documents with required fields
        processed_docs = processed_collection.count_documents({'is_valid': True})
        sentiment_docs = processed_collection.count_documents({'is_analyzed_for_sentiment': True})
        entity_docs = processed_collection.count_documents({'entities.label': {'$in': entity_types}})
        logger.info(f"Processed documents: {processed_docs}")
        logger.info(f"Sentiment-analyzed documents: {sentiment_docs}")
        logger.info(f"Documents with entities {entity_types}: {entity_docs}")

        # Query comments with entities and sentiment
        cursor = processed_collection.find({
            'processed_at': {'$gte': cutoff},
            'entities.label': {'$in': entity_types},
            'is_analyzed_for_sentiment': True,
            'is_valid': True
        }).batch_size(1000)

        # Aggregate trends (general and per sport type)
        entity_counts = defaultdict(int)
        sentiment_scores = defaultdict(list)
        entity_sport_types = defaultdict(Counter)
        entity_trend_details = defaultdict(lambda: defaultdict(int))
        sport_type_trends_data = defaultdict(lambda: {
            'entity_counts': defaultdict(int),
            'sentiment_scores': defaultdict(list),
            'trend_details': defaultdict(lambda: defaultdict(int)),
            'sample_comments': defaultdict(list)  # Store comments per entity per sport type
        })
        comment_count = 0

        for doc in cursor:
            comment_count += 1
            raw_data_id = doc.get('raw_data')
            sport_type = "unknown"
            raw_text = "غير متوفر"
            author_name = "غير متوفر"
            if raw_data_id:
                try:
                    raw_doc = rawdata_collection.find_one({'_id': ObjectId(raw_data_id)})
                    if raw_doc:
                        sport_type = raw_doc.get('sport_type', 'unknown')
                        raw_text = raw_doc.get('content', 'غير متوفر')
                        author_name = raw_doc.get('author_name', 'غير متوفر')
                except Exception as e:
                    logger.warning(f"Error fetching raw_data {raw_data_id}: {str(e)}")

            entities = doc.get('entities', [])
            sentiment = doc.get('sentiment', {})
            sentiment_label = sentiment.get('label', 'LABEL_2')
            mapped_sentiment = sentiment_map.get(sentiment_label, 'neutral')
            sentiment_score = sentiment.get('score', 0.0)
            doc_date = doc.get('processed_at', start_time).date()
            comment_date = doc.get('processed_at', start_time).strftime('%Y-%m-%d %H:%M:%S')

            # Prepare comment data
            comment_data = {
                "text": raw_text,
                "sentiment": mapped_sentiment,
                "sentiment_score": sentiment_score,
                "date": comment_date,
                "sport_type": sport_type,
                "author_name": author_name
            }

            for entity in entities:
                if entity['label'] in entity_types:
                    entity_text = entity['text']
                    entity_key = (entity['label'], entity_text)
                    # General trends
                    entity_counts[entity_key] += 1
                    sentiment_scores[entity_key].append({
                        'text': mapped_sentiment,
                        'score': sentiment_score
                    })
                    entity_sport_types[entity_key][sport_type] += 1
                    entity_trend_details[entity_key][doc_date.strftime('%Y-%m-%d')] += 1
                    # Sport-specific trends
                    sport_type_trends_data[sport_type]['entity_counts'][entity_key] += 1
                    sport_type_trends_data[sport_type]['sentiment_scores'][entity_key].append({
                        'text': mapped_sentiment,
                        'score': sentiment_score
                    })
                    sport_type_trends_data[sport_type]['trend_details'][entity_key][doc_date.strftime('%Y-%m-%d')] += 1
                    # Store sample comments (keep only the 5 most recent)
                    comments_list = sport_type_trends_data[sport_type]['sample_comments'][entity_key]
                    comments_list.append(comment_data)
                    # Sort by date (descending) and keep only the 5 most recent
                    comments_list.sort(key=lambda x: x['date'], reverse=True)
                    sport_type_trends_data[sport_type]['sample_comments'][entity_key] = comments_list[:5]

        if comment_count == 0:
            logger.warning("No comments found matching criteria")
            client.close()
            return {"status": "no_data", "trends": [], "time_window_days": time_window_days}

        # Process general trends (limit to top 10)
        trends = []
        for (entity_type, entity_text), count in entity_counts.items():
            sentiments = sentiment_scores[(entity_type, entity_text)]
            sentiment_summary = {
                'positive': sum(1 for s in sentiments if s['text'] == 'positive'),
                'neutral': sum(1 for s in sentiments if s['text'] == 'neutral'),
                'negative': sum(1 for s in sentiments if s['text'] == 'negative'),
                'average_score': sum(s['score'] for s in sentiments) / len(sentiments) if sentiments else 0.0
            }
            entity_key = (entity_type, entity_text)
            dominant_sport = entity_sport_types[entity_key].most_common(1)[0][0] if entity_sport_types[entity_key] else 'unknown'
            trend_details = []
            current_date = (start_time - timedelta(days=time_window_days)).date()
            end_date = start_time.date()
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                mentions = entity_trend_details[entity_key][date_str]
                trend_details.append({
                    "date": date_str,
                    "mentions": mentions
                })
                current_date += timedelta(days=1)
            trends.append({
                'entity_type': entity_type,
                'entity_text': entity_text,
                'count': count,
                'sentiment': sentiment_summary,
                'sport_type': dominant_sport,
                'trend_details': trend_details
            })

        trends.sort(key=lambda x: x['count'], reverse=True)
        trends = trends[:10]  # Limit to top 10
        logger.info(f"Saving top {len(trends)} general trends")

        # Process sport-specific most mentioned entities
        sport_type_trends = {}
        for sport_type, data in sport_type_trends_data.items():
            # Initialize counters for each entity type within this sport
            player_counts = Counter()
            team_counts = Counter()
            competition_counts = Counter()

            # Aggregate counts for each entity type
            for (entity_type, entity_text), count in data['entity_counts'].items():
                if entity_type == 'PLAYER':
                    player_counts[entity_text] = count
                elif entity_type == 'TEAM':
                    team_counts[entity_text] = count
                elif entity_type == 'COMPETITION':
                    competition_counts[entity_text] = count

            # Helper function to build trend details for an entity
            def get_sport_trend_details(entity_type, entity_text):
                entity_key = (entity_type, entity_text)
                trend_details = []
                current_date = (start_time - timedelta(days=time_window_days)).date()
                end_date = start_time.date()
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    mentions = data['trend_details'][entity_key][date_str]
                    trend_details.append({
                        "date": date_str,
                        "mentions": mentions
                    })
                    current_date += timedelta(days=1)
                return trend_details

            # Helper function to compute sentiment summary for an entity
            def get_sentiment_summary(entity_type, entity_text):
                entity_key = (entity_type, entity_text)
                sentiments = data['sentiment_scores'][entity_key]
                return {
                    'positive': sum(1 for s in sentiments if s['text'] == 'positive'),
                    'neutral': sum(1 for s in sentiments if s['text'] == 'neutral'),
                    'negative': sum(1 for s in sentiments if s['text'] == 'negative'),
                    'average_score': sum(s['score'] for s in sentiments) / len(sentiments) if sentiments else 0.0
                }

            # Most mentioned player for this sport
            most_mentioned_player = {}
            if player_counts:
                player_text, player_count = player_counts.most_common(1)[0]
                most_mentioned_player = {
                    "entity_text": player_text,
                    "count": player_count,
                    "trend_details": get_sport_trend_details('PLAYER', player_text),
                    "sample_comments": data['sample_comments'][('PLAYER', player_text)],
                    "sentiment": get_sentiment_summary('PLAYER', player_text)
                }
            else:
                most_mentioned_player = {
                    "entity_text": "غير متوفر",
                    "count": 0,
                    "trend_details": [],
                    "sample_comments": [],
                    "sentiment": {"positive": 0, "neutral": 0, "negative": 0, "average_score": 0.0}
                }

            # Most mentioned team for this sport
            most_mentioned_team = {}
            if team_counts:
                team_text, team_count = team_counts.most_common(1)[0]
                most_mentioned_team = {
                    "entity_text": team_text,
                    "count": team_count,
                    "trend_details": get_sport_trend_details('TEAM', team_text),
                    "sample_comments": data['sample_comments'][('TEAM', team_text)],
                    "sentiment": get_sentiment_summary('TEAM', team_text)
                }
            else:
                most_mentioned_team = {
                    "entity_text": "غير متوفر",
                    "count": 0,
                    "trend_details": [],
                    "sample_comments": [],
                    "sentiment": {"positive": 0, "neutral": 0, "negative": 0, "average_score": 0.0}
                }

            # Most mentioned competition for this sport
            most_mentioned_competition = {}
            if competition_counts:
                competition_text, competition_count = competition_counts.most_common(1)[0]
                most_mentioned_competition = {
                    "entity_text": competition_text,
                    "count": competition_count,
                    "trend_details": get_sport_trend_details('COMPETITION', competition_text),
                    "sample_comments": data['sample_comments'][('COMPETITION', competition_text)],
                    "sentiment": get_sentiment_summary('COMPETITION', competition_text)
                }
            else:
                most_mentioned_competition = {
                    "entity_text": "غير متوفر",
                    "count": 0,
                    "trend_details": [],
                    "sample_comments": [],
                    "sentiment": {"positive": 0, "neutral": 0, "negative": 0, "average_score": 0.0}
                }

            # Store the most mentioned entities for this sport type
            sport_type_trends[sport_type] = {
                "PLAYER": most_mentioned_player,
                "TEAM": most_mentioned_team,
                "COMPETITION": most_mentioned_competition
            }
            logger.info(f"Saved most mentioned entities with sentiment for sport_type: {sport_type}")

        # Compute dashboard stats
        total_posts = processed_collection.count_documents({'is_valid': True})

        # Most popular hashtag
        hashtag_counts = Counter()
        comments = processed_collection.find({'is_valid': True, 'raw_data': {'$exists': True}})
        for comment in comments:
            raw_data_id = comment.get('raw_data')
            raw_text = ""
            if raw_data_id:
                try:
                    raw_doc = rawdata_collection.find_one({'_id': ObjectId(raw_data_id)})
                    raw_text = raw_doc.get('content', '') if raw_doc else ''
                except Exception as e:
                    logger.warning(f"Error fetching raw_data {raw_data_id}: {str(e)}")
            hashtags = re.findall(r'#[\w]+', raw_text, re.UNICODE)
            hashtag_counts.update(hashtags)
        most_popular_hashtag = hashtag_counts.most_common(1)[0][0] if hashtag_counts else "غير متوفر"

        # Most mentioned entities with trend details (global)
        player_counts = Counter()
        team_counts = Counter()
        competition_counts = Counter()
        for (entity_type, entity_text), count in entity_counts.items():
            if entity_type == 'PLAYER':
                player_counts[entity_text] = count
            elif entity_type == 'TEAM':
                team_counts[entity_text] = count
            elif entity_type == 'COMPETITION':
                competition_counts[entity_text] = count

        # Helper function to build trend details for an entity (global)
        def get_trend_details(entity_type, entity_text):
            entity_key = (entity_type, entity_text)
            trend_details = []
            current_date = (start_time - timedelta(days=time_window_days)).date()
            end_date = start_time.date()
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                mentions = entity_trend_details[entity_key][date_str]
                trend_details.append({
                    "date": date_str,
                    "mentions": mentions
                })
                current_date += timedelta(days=1)
            return trend_details

        # Most mentioned player (global)
        most_mentioned_player = {}
        if player_counts:
            player_text, player_count = player_counts.most_common(1)[0]
            most_mentioned_player = {
                "entity_text": player_text,
                "count": player_count,
                "trend_details": get_trend_details('PLAYER', player_text)
            }
        else:
            most_mentioned_player = {"entity_text": "غير متوفر", "count": 0, "trend_details": []}

        # Most mentioned team (global)
        most_mentioned_team = {}
        if team_counts:
            team_text, team_count = team_counts.most_common(1)[0]
            most_mentioned_team = {
                "entity_text": team_text,
                "count": team_count,
                "trend_details": get_trend_details('TEAM', team_text)
            }
        else:
            most_mentioned_team = {"entity_text": "غير متوفر", "count": 0, "trend_details": []}

        # Most mentioned competition (global)
        most_mentioned_competition = {}
        if competition_counts:
            competition_text, competition_count = competition_counts.most_common(1)[0]
            most_mentioned_competition = {
                "entity_text": competition_text,
                "count": competition_count,
                "trend_details": get_trend_details('COMPETITION', competition_text)
            }
        else:
            most_mentioned_competition = {"entity_text": "غير متوفر", "count": 0, "trend_details": []}

        # Overall sentiment
        overall_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
        comments = processed_collection.find({'is_analyzed_for_sentiment': True, 'is_valid': True})
        for comment in comments:
            sentiment = comment.get('sentiment', {})
            sentiment_label = sentiment.get('label', 'LABEL_2')
            mapped_sentiment = sentiment_map.get(sentiment_label, 'neutral')
            overall_sentiment[mapped_sentiment] += 1

        # Word cloud
        word_counts = Counter()
        stop_words = set([
            'في', 'على', 'من', 'إلى', 'عن', 'مع', 'و', 'أو', 'لكن', 'ثم',
            'هذا', 'هذه', 'ذلك', 'تلك', 'كل', 'بعد', 'قبل', 'أن', 'لا'
        ])
        comments = processed_collection.find({'is_valid': True, 'normalized_text': {'$exists': True}})
        for comment in comments:
            text = comment.get('normalized_text', '')
            tokens = simple_word_tokenize(text)
            tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
            word_counts.update(tokens)
        word_cloud = [{"word": word, "count": count} for word, count in word_counts.most_common(50)]

        # Detailed stats
        detailed_stats = {}
        for etype in entity_types:
            etype_counts = sum(count for (t, _), count in entity_counts.items() if t == etype)
            etype_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
            for (t, txt), sents in sentiment_scores.items():
                if t == etype:
                    for s in sents:
                        etype_sentiment[s['text']] += 1

            etype_entity_counts = Counter({txt: count for (t, txt), count in entity_counts.items() if t == etype})
            most_mentioned = etype_entity_counts.most_common(1)[0][0] if etype_entity_counts else "غير متوفر"

            trend_data = []
            current_date = start_time - timedelta(days=time_window_days)
            end_date = start_time
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                count = processed_collection.count_documents({
                    'processed_at': {'$gte': current_date, '$lt': next_date},
                    f'entities.label': etype
                })
                trend_data.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "mentions": count
                })
                current_date = next_date

            sample_posts = []
            recent_comments = processed_collection.find({
                f'entities.label': etype,
                f'entities.text': most_mentioned,
                'is_valid': True
            }).sort('processed_at', -1).limit(5)
            for comment in recent_comments:
                raw_data_id = comment.get('raw_data')
                text = "غير متوفر"
                sport_type = "unknown"
                author_name = "غير متوفر"
                if raw_data_id:
                    try:
                        raw_doc = rawdata_collection.find_one({'_id': ObjectId(raw_data_id)})
                        text = raw_doc.get('content', 'غير متوفر') if raw_doc else 'غير متوفر'
                        sport_type = raw_doc.get('sport_type', 'unknown') if raw_doc else 'unknown'
                        author_name = raw_doc.get('author_name', 'غير متوفر') if raw_doc else 'غير متوفر'
                    except Exception as e:
                        logger.warning(f"Error fetching raw_data {raw_data_id}: {str(e)}")
                sentiment = comment.get('sentiment', {})
                sentiment_label = sentiment.get('label', 'LABEL_2')
                mapped_sentiment = sentiment_map.get(sentiment_label, 'neutral')
                sentiment_score = comment.get('sentiment', {}).get('score', 0.0)
                sample_posts.append({
                    "text": text,
                    "sentiment": mapped_sentiment,
                    "sentiment_score": sentiment_score,
                    "date": comment.get('processed_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S'),
                    "sport_type": sport_type,
                    "author_name": author_name
                })

            detailed_stats[etype] = {
                "total_mentions": etype_counts,
                "sentiment_analysis": etype_sentiment,
                "most_mentioned_entity": most_mentioned,
                "trend_details": trend_data,
                "sample_posts": sample_posts
            }

        # Insert into trends collection
        db['trends'].insert_one({
            'analysis_time': start_time,
            'time_window_days': time_window_days,
            'entity_types': entity_types,
            'trends': trends,
            'comment_count': comment_count,
            'sport_type_trends': sport_type_trends,
            'dashboard_stats': {
                "total_posts": total_posts,
                "most_popular_hashtag": most_popular_hashtag,
                "most_mentioned_player": most_mentioned_player,
                "most_mentioned_team": most_mentioned_team,
                "most_mentioned_competition": most_mentioned_competition,
                "sentiment_analysis": overall_sentiment,
                "word_cloud": word_cloud
            },
            'detailed_stats': detailed_stats
        })

        client.close()
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Trend analysis completed: {comment_count} comments, {len(trends)} trends in {duration:.2f} seconds")

        return {
            "status": "success",
            "trends": trends[:10],
            "comment_count": comment_count,
            "time_window_days": time_window_days
        }

    except Exception as e:
        logger.error(f"Trend analysis failed: {str(e)}", exc_info=True)
        raise