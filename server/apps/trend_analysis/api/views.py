# apps/trend_analysis/api/views.py
from django.http import JsonResponse
from pymongo import MongoClient
from django.conf import settings
import logging
        
from django.http import JsonResponse
from django.conf import settings
from pymongo import MongoClient
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

logger = logging.getLogger(__name__)

def get_dashboard_stats(request):
    """
    Endpoint to fetch precomputed dashboard statistics from the trends collection.
    
    Returns:
        JSON response with total posts, most popular hashtag, most mentioned entities,
        sentiment analysis, and word cloud data.
    """
    try:
        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        trends_collection = db['trends']
        logger.debug("Connected to MongoDB for dashboard stats")

        # Fetch the latest trends document
        trends_doc = trends_collection.find_one(
            {},
            sort=[('analysis_time', -1)]
        )

        if not trends_doc or 'dashboard_stats' not in trends_doc:
            client.close()
            return JsonResponse({
                "status": "error",
                "message": "No precomputed dashboard stats available."
            }, status=404)

        dashboard_stats = trends_doc['dashboard_stats']
        response = {
            "total_posts": dashboard_stats.get('total_posts', 0),
            "most_popular_hashtag": dashboard_stats.get('most_popular_hashtag', 'غير متوفر'),
            "most_mentioned_player": dashboard_stats.get('most_mentioned_player', 'غير متوفر'),
            "most_mentioned_team": dashboard_stats.get('most_mentioned_team', 'غير متوفر'),
            "most_mentioned_competition": dashboard_stats.get('most_mentioned_competition', 'غير متوفر'),
            "sentiment_analysis": dashboard_stats.get('sentiment_analysis', {'positive': 0, 'negative': 0, 'neutral': 0}),
            "word_cloud": dashboard_stats.get('word_cloud', [])
        }

        client.close()
        logger.info("Dashboard stats fetched successfully")
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {str(e)}", exc_info=True)
        client.close()
        return JsonResponse({
            "status": "error",
            "message": f"Failed to fetch dashboard stats: {str(e)}"
        }, status=500)

def get_detailed_dashboard_stats(request):
    """
    Endpoint to fetch precomputed detailed dashboard statistics for the frontend, filtered by entity type.

    Query Parameters:
        entity_type (str): Entity type to filter by ('PLAYER', 'COMPETITION', 'TEAM').

    Returns:
        JSON response with trend details, sentiment analysis, sample posts, and additional stats.
    """
    try:
        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        trends_collection = db['trends']
        logger.debug("Connected to MongoDB for detailed dashboard stats")

        # Get entity type from query parameters
        entity_type = request.GET.get('entity_type', 'PLAYER').upper()
        if entity_type not in ['PLAYER', 'COMPETITION', 'TEAM']:
            client.close()
            return JsonResponse({
                "status": "error",
                "message": "Invalid entity_type. Must be 'PLAYER', 'COMPETITION', or 'TEAM'."
            }, status=400)

        # Fetch the latest trends document
        trends_doc = trends_collection.find_one(
            {'entity_types': entity_type},
            sort=[('analysis_time', -1)]
        )

        if not trends_doc or 'detailed_stats' not in trends_doc or entity_type not in trends_doc['detailed_stats']:
            client.close()
            return JsonResponse({
                "status": "error",
                "message": f"No precomputed detailed stats available for entity_type: {entity_type}."
            }, status=404)

        # Fetch overall stats for most_popular_hashtag
        overall_stats = trends_doc['dashboard_stats']
        detailed_stats = trends_doc['detailed_stats'][entity_type]

        response = {
            "total_mentions": detailed_stats.get('total_mentions', 0),
            "most_popular_hashtag": overall_stats.get('most_popular_hashtag', 'غير متوفر'),
            "most_mentioned_entity": detailed_stats.get('most_mentioned_entity', 'غير متوفر'),
            "sentiment_analysis": detailed_stats.get('sentiment_analysis', {'positive': 0, 'negative': 0, 'neutral': 0}),
            "trend_details": detailed_stats.get('trend_details', []),
            "sample_posts": detailed_stats.get('sample_posts', []),
            "entity_type": entity_type
        }

        client.close()
        logger.info("Detailed dashboard stats fetched successfully")
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        logger.error(f"Error in get_detailed_dashboard_stats: {str(e)}", exc_info=True)
        client.close()
        return JsonResponse({
            "status": "error",
            "message": f"Failed to fetch detailed dashboard stats: {str(e)}"
        }, status=500)
        


def get_trend_by_sports_type(request):
    """
    Endpoint to fetch trend data filtered by sports type and entity type.

    Query Parameters:
        sport_type (str): Sports type to filter by (e.g., 'كرة_القدم', 'كرة_السلة').
        entity_type (str, optional): Entity type to filter by (e.g., 'PLAYER', 'TEAM', 'COMPETITION').

    Returns:
        JSON response with trend data for the specified sports type and entity type.
    """
    try:
        # Get the sport_type from query parameters
        sport_type = request.GET.get('sport_type')
        if not sport_type:
            return JsonResponse(
                {"status": "error", "message": "sport_type parameter is required"},
                status=400
            )

        # Get the entity_type from query parameters (optional)
        entity_type = request.GET.get('entity_type')
        valid_entity_types = ['PLAYER', 'TEAM', 'COMPETITION']
        if entity_type and entity_type not in valid_entity_types:
            return JsonResponse(
                {"status": "error", "message": f"Invalid entity_type. Must be one of {valid_entity_types}"},
                status=400
            )

        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        trends_collection = db['trends']

        # Fetch the latest trends document
        latest_trends = trends_collection.find_one(
            {},
            sort=[('analysis_time', -1)]
        )

        if not latest_trends:
            client.close()
            return JsonResponse(
                {"status": "error", "message": "No trends data available"},
                status=404
            )

        # Get sport-specific trends
        sport_type_trends = latest_trends.get('sport_type_trends', {})
        trends = sport_type_trends.get(sport_type, {
            "PLAYER": {"entity_text": "غير متوفر", "count": 0, "trend_details": []},
            "TEAM": {"entity_text": "غير متوفر", "count": 0, "trend_details": []},
            "COMPETITION": {"entity_text": "غير متوفر", "count": 0, "trend_details": []}
        })

        # Filter by entity_type if provided
        if entity_type:
            trend_data = trends.get(entity_type, {"entity_text": "غير متوفر", "count": 0, "trend_details": []})
            if trend_data["entity_text"] == "غير متوفر":
                client.close()
                return JsonResponse(
                    {"status": "success", "message": f"No {entity_type} data found for sport_type: {sport_type}"},
                    status=200
                )
            client.close()
            return JsonResponse(trend_data, safe=False, status=200)

        # If no entity_type is provided, return all trends for the sport_type
        if trends == {
            "PLAYER": {"entity_text": "غير متوفر", "count": 0, "trend_details": []},
            "TEAM": {"entity_text": "غير متوفر", "count": 0, "trend_details": []},
            "COMPETITION": {"entity_text": "غير متوفر", "count": 0, "trend_details": []}
        }:
            client.close()
            return JsonResponse(
                {"status": "success", "message": f"No trends found for sport_type: {sport_type}"},
                status=200
            )

        client.close()
        return JsonResponse(trends, safe=False, status=200)

    except Exception as e:
        logger.error(f"Error fetching trends for sport_type {sport_type}: {str(e)}", exc_info=True)
        return JsonResponse(
            {"status": "error", "message": "An error occurred while fetching trends"},
            status=500
        )