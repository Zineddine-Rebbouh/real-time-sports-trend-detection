# # apps/data_collection/tasks.py
# from celery import shared_task
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from django.conf import settings
# from apps.data_collection.models import RawData, DataSource
# from pymongo import MongoClient
# import logging
# import time
# import random
# from datetime import datetime

# logger = logging.getLogger(__name__)

# # Sports lexicon (from March 30, 2025 hashtag list and April 1, 2025 entities)
# SPORTS_LEXICON = {
#     'keywords': [
#         'كرة القدم', 'كرة السلة', 'تنس', 'ملاكمة', 'كرة الطائرة', 'سباحة',
#         'ألعاب القوى', 'جودو', 'كاراتيه', 'مصارعة', 'ركوب الدراجات',
#         'هوكي', 'كرة اليد', 'جمباز', 'رفع الأثقال'
#     ],
#     'players': [
#         'محمد صلاح', 'ليونيل ميسي', 'كريستيانو رونالدو', 'كريم بنزيما',
#         'نيمار', 'كيليان مبابي', 'سامي الجابر'
#     ],
#     'teams': [
#         'الهلال', 'النصر', 'الأهلي', 'ريال مدريد', 'برشلونة',
#         'منتخب مصر', 'منتخب السعودية', 'منتخب الكويت'
#     ],
#     'competitions': [
#         'كأس العالم', 'دوري أبطال أوروبا', 'الدوري الإسباني',
#         'الدوري السعودي', 'كأس أمم إفريقيا', 'كأس الخليج'
#     ]
# }

# # Regex patterns for filtering
# ARABIC_PATTERN = r'^[\u0600-\u06FF\s\w.,!?]*$'  # Arabic characters, spaces, basic punctuation
# EMOJI_PATTERN = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]'  # Emojis
# HASHTAG_PATTERN = r'#[\w_]+'  # Extract hashtags
# SPAM_PATTERN = r'^(?:http|www|\d{5,}|.{0,10})$'  # URLs, numbers, short text

# def get_youtube_datasource():
#     """Fetch active YouTube DataSource using pymongo."""
#     try:
#         sources = [{
#                "collection_rules": {
#                    "keywords": SPORTS_LEXICON['keywords'],
#                    "max_videos": 10,
#                    "max_comments": 50,
#                    "min_likes": 1
#                }
#            }]        
#         return list(sources)
#     except Exception as e:
#         logger.error(f"Error querying DataSource: {str(e)}")
#         return []
   


# @shared_task
# def collect_youtube_data():
#     """Collect raw YouTube comments and save to RawData."""
#     try:
#         youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
#         sources = get_youtube_datasource()
#         if not sources:
#             logger.warning("No active YouTube DataSource, using default rules")
#             sources = [{
#                 "collection_rules": {
#                     "keywords": SPORTS_LEXICON['keywords'],
#                     "max_videos": 10,
#                     "max_comments": 50,
#                     "min_likes": 1
#                 }
#             }]

#         total_comments = 0
#         for source in sources:
#             keywords = source['collection_rules'].get('keywords', SPORTS_LEXICON['keywords'])
#             max_videos = source['collection_rules'].get('max_videos', 10)
#             max_comments_per_video = source['collection_rules'].get('max_comments', 50)

#             for query in keywords:
#                 logger.info(f"Searching YouTube videos for query: {query}")
#                 try:
#                     search_response = youtube.search().list(
#                         q=query,
#                         type='video',
#                         part='id,snippet',
#                         maxResults=max_videos,
#                         relevanceLanguage='ar',
#                         order='relevance'
#                     ).execute()
#                     video_ids = [
#                         item['id']['videoId'] for item in search_response.get('items', [])
#                         if 'snippet' in item and 'title' in item['snippet']
#                         and any(kw.lower() in item['snippet']['title'].lower() for kw in SPORTS_LEXICON['keywords'])
#                     ]
#                     logger.info(f"Found {len(video_ids)} relevant videos for query: {query}")
#                 except HttpError as e:
#                     logger.error(f"Error searching videos for {query}: {str(e)}")
#                     continue

#                 for video_id in video_ids:
#                     logger.info(f"Collecting comments for video: {video_id}")
#                     comments = []
#                     try:
#                         request = youtube.commentThreads().list(
#                             part='snippet',
#                             videoId=video_id,
#                             maxResults=50,
#                             textFormat='plainText',
#                             order='relevance'
#                         )
#                         response = request.execute()

#                         for item in response['items']:
#                             comment = item['snippet']['topLevelComment']['snippet']
#                             comments.append({
#                                 'text': comment['textDisplay'],
#                                 'likes': comment.get('likeCount', 0),
#                                 'published_at': comment['publishedAt'],
#                                 'author': comment['authorDisplayName']
#                             })

#                         while len(comments) < max_comments_per_video and 'nextPageToken' in response:
#                             request = youtube.commentThreads().list(
#                                 part='snippet',
#                                 videoId=video_id,
#                                 pageToken=response['nextPageToken'],
#                                 maxResults=50,
#                                 textFormat='plainText',
#                                 order='relevance'
#                             )
#                             response = request.execute()
#                             for item in response['items']:
#                                 comment = item['snippet']['topLevelComment']['snippet']
#                                 comments.append({
#                                     'text': comment['textDisplay'],
#                                     'likes': comment.get('likeCount', 0),
#                                     'published_at': comment['publishedAt'],
#                                     'author': comment['authorDisplayName']
#                                 })
#                                 if len(comments) >= max_comments_per_video:
#                                     break

#                         # Save raw comments to RawData
#                         client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
#                         db = client[settings.DATABASES['default']['NAME']]
#                         for comment in comments:
#                             try:
#                                 source_id = f"{video_id}_{hash(comment['text'])}"
#                                 existing = db['data_collection_rawdata'].find_one({'source_id': source_id})
#                                 if not existing:
#                                     db['data_collection_rawdata'].insert_one({
#                                         'source': 'youtube',
#                                         'source_id': source_id,
#                                         'content': comment['text'],
#                                         'author_id': '',
#                                         'author_name': comment['author'],
#                                         'author_followers': 0,
#                                         'author_verified': False,
#                                         'likes': comment['likes'],
#                                         'shares': 0,
#                                         'language': 'ar',
#                                         'hashtags': [],  # Hashtags will be extracted during cleaning
#                                         'created_at': datetime.strptime(
#                                             comment['published_at'], '%Y-%m-%dT%H:%M:%SZ'
#                                         ),
#                                         'is_processed': False,
#                                         'is_cleaned': False  # New field to track cleaning status
#                                     })
#                                     logger.info(f"Saved raw comment {source_id} to RawData")
#                                     total_comments += 1
#                                 else:
#                                     logger.info(f"Raw comment {source_id} already exists")
#                             except Exception as e:
#                                 logger.error(f"Error saving raw comment for video {video_id}: {str(e)}")

#                         logger.info(f"Collected {len(comments)} raw comments for video: {video_id}")
#                         time.sleep(random.randint(1, 2))

#                     except HttpError as e:
#                         logger.error(f"Error fetching comments for video {video_id}: {str(e)}")
#                         continue

#                 time.sleep(random.randint(2, 5))

#         return f"Collected {total_comments} new raw YouTube comments"
#     except Exception as e:
#         logger.error(f"Error in collect_youtube_data: {str(e)}")
#         raise


# apps/data_collection/tasks.py
from celery import shared_task
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from pymongo import MongoClient
import logging
import time
import random
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# Sports lexicon (from March 30, 2025 hashtag list and April 1, 2025 entities)
SPORTS_LEXICON = {
    'keywords': [
        'كرة القدم', 'كرة السلة', 'تنس', 'ملاكمة', 'كرة الطائرة', 'سباحة',
        'ألعاب القوى', 'جودو', 'كاراتيه', 'مصارعة', 'ركوب الدراجات',
        'هوكي', 'كرة اليد', 'جمباز', 'رفع الأثقال'
    ],
    'players': [
        'محمد صلاح', 'ليونيل ميسي', 'كريستيانو رونالدو', 'كريم بنزيما',
        'نيمار', 'كيليان مبابي', 'سامي الجابر'
    ],
    'teams': [
        'الهلال', 'النصر', 'الأهلي', 'ريال مدريد', 'برشلونة',
        'منتخب مصر', 'منتخب السعودية', 'منتخب الكويت'
    ],
    'competitions': [
        'كأس العالم', 'دوري أبطال أوروبا', 'الدوري الإسباني',
        'الدوري السعودي', 'كأس أمم إفريقيا', 'كأس الخليج'
    ]
}

# Regex patterns for filtering
ARABIC_PATTERN = r'^[\u0600-\u06FF\s\w.,!?]*$'  # Arabic characters, spaces, basic punctuation
EMOJI_PATTERN = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]'  # Emojis
HASHTAG_PATTERN = r'#[\w_]+'  # Extract hashtags
SPAM_PATTERN = r'^(?:http|www|\d{5,}|.{0,10})$'  # URLs, numbers, short text

# Sports-related hashtags for queries
SPORTS_QUERIES = [
    "#رياضة", "#كرة_القدم", "#كرة_السلة" ,"NBA", "#تنس", "#ملاكمة", "#كرة_الطائرة",
]

def get_youtube_datasource():
    """Fetch active YouTube DataSource using pymongo."""
    try:
        sources = [{
            "collection_rules": {
                "keywords": SPORTS_QUERIES,
                "max_videos": 10,
                "max_comments": 50,
                "min_likes": 1
            }
        }]
        return list(sources)
    except Exception as e:
        logger.error(f"Error querying DataSource: {str(e)}")
        return []

@shared_task
def collect_youtube_data():
    """Collect raw YouTube comments and save to RawData with sport type based on query hashtag."""
    client = None
    try:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        sources = get_youtube_datasource()
        if not sources:
            logger.warning("No active YouTube DataSource, using default rules")
            sources = [{
                "collection_rules": {
                    "keywords": SPORTS_QUERIES,
                    "max_videos": 10,
                    "max_comments": 50,
                    "min_likes": 1
                }
            }]

        total_comments = 0
        for source in sources:
            keywords = source['collection_rules'].get('keywords', SPORTS_QUERIES)
            max_videos = source['collection_rules'].get('max_videos', 10)
            max_comments_per_video = source['collection_rules'].get('max_comments', 50)
            min_likes = source['collection_rules'].get('min_likes', 1)

            # Use SPORTS_QUERIES directly for search
            search_queries = keywords

            for query in search_queries:
                # Extract sport type from the query hashtag (e.g., #كرة_القدم -> كرة_القدم)
                sport_type = query.replace('#', '')
                logger.info(f"Searching YouTube videos for query: {query} (Sport Type: {sport_type})")
                try:
                    search_response = youtube.search().list(
                        q=query,
                        type='video',
                        part='id,snippet',
                        maxResults=max_videos,
                        relevanceLanguage='ar',
                        order='relevance'
                    ).execute()
                    video_ids = [
                        item['id']['videoId'] for item in search_response.get('items', [])
                        if 'snippet' in item and 'title' in item['snippet']
                    ]
                    logger.info(f"Found {len(video_ids)} relevant videos for query: {query}")
                except HttpError as e:
                    if 'quotaExceeded' in str(e):
                        logger.error(f"Quota exceeded for YouTube API. Please wait until the quota resets or increase your quota.")
                    else:
                        logger.error(f"Error searching videos for {query}: {str(e)}")
                    continue

                for video_id in video_ids:
                    logger.info(f"Collecting comments for video: {video_id}")
                    comments = []
                    try:
                        request = youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=50,
                            textFormat='plainText',
                            order='relevance'
                        )
                        response = request.execute()

                        for item in response['items']:
                            comment = item['snippet']['topLevelComment']['snippet']
                            comment_text = comment['textDisplay']
                            likes = comment.get('likeCount', 0)

                            # Skip comments with insufficient likes
                            if likes < min_likes:
                                continue

                            # Check for spam
                            if re.match(SPAM_PATTERN, comment_text.lower()):
                                logger.debug(f"Skipping spam comment: {comment_text}")
                                continue

                            comments.append({
                                'text': comment_text,
                                'likes': likes,
                                'published_at': comment['publishedAt'],
                                'author': comment['authorDisplayName']
                            })

                        # Fetch more comments if needed
                        while len(comments) < max_comments_per_video and 'nextPageToken' in response:
                            request = youtube.commentThreads().list(
                                part='snippet',
                                videoId=video_id,
                                pageToken=response['nextPageToken'],
                                maxResults=50,
                                textFormat='plainText',
                                order='relevance'
                            )
                            response = request.execute()
                            for item in response['items']:
                                comment = item['snippet']['topLevelComment']['snippet']
                                comment_text = comment['textDisplay']
                                likes = comment.get('likeCount', 0)

                                if likes < min_likes:
                                    continue

                                if re.match(SPAM_PATTERN, comment_text.lower()):
                                    logger.debug(f"Skipping spam comment: {comment_text}")
                                    continue

                                comments.append({
                                    'text': comment_text,
                                    'likes': likes,
                                    'published_at': comment['publishedAt'],
                                    'author': comment['authorDisplayName']
                                })
                                if len(comments) >= max_comments_per_video:
                                    break

                        # Initialize MongoDB client if not already done
                        if not client:
                            client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
                        db = client[settings.DATABASES['default']['NAME']]

                        # Save raw comments to RawData
                        for comment in comments:
                            try:
                                source_id = f"{video_id}_{hash(comment['text'])}"
                                existing = db['data_collection_rawdata'].find_one({'source_id': source_id})
                                if not existing:
                                    # Extract hashtags from the comment
                                    hashtags = re.findall(HASHTAG_PATTERN, comment['text'], re.UNICODE)
                                    hashtags = [h.lower() for h in hashtags]

                                    db['data_collection_rawdata'].insert_one({
                                        'source': 'youtube',
                                        'source_id': source_id,
                                        'content': comment['text'],
                                        'author_id': '',
                                        'author_name': comment['author'],
                                        'author_followers': 0,
                                        'author_verified': False,
                                        'likes': comment['likes'],
                                        'shares': 0,
                                        'language': 'ar',
                                        'hashtags': hashtags,
                                        'sport_type': sport_type,
                                        'created_at': datetime.strptime(
                                            comment['published_at'], '%Y-%m-%dT%H:%M:%SZ'
                                        ),
                                        'is_processed': False,
                                        'is_cleaned': False
                                    })
                                    logger.info(f"Saved raw comment {source_id} to RawData with sport_type: {sport_type}, hashtags: {hashtags}")
                                    total_comments += 1
                                else:
                                    logger.info(f"Raw comment {source_id} already exists")
                            except Exception as e:
                                logger.error(f"Error saving raw comment for video {video_id}: {str(e)}")

                        logger.info(f"Collected {len(comments)} raw comments for video: {video_id}")
                        time.sleep(random.randint(1, 2))

                    except HttpError as e:
                        if 'quotaExceeded' in str(e):
                            logger.error(f"Quota exceeded while fetching comments for video {video_id}. Skipping.")
                        else:
                            logger.error(f"Error fetching comments for video {video_id}: {str(e)}")
                        continue

                time.sleep(random.randint(2, 5))

        return f"Collected {total_comments} new raw YouTube comments"
    except Exception as e:
        logger.error(f"Error in collect_youtube_data: {str(e)}")
        raise
    finally:
        if client:
            client.close()
            logger.debug("MongoDB client closed")