# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.trend_analysis.api.views import get_dashboard_stats , get_detailed_dashboard_stats ,get_trend_by_sports_type

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # JWT authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Your app URLs
    path('api/data-collection/', include('apps.data_collection.api.urls')),
    path('api/text-processing/', include('apps.text_processing.api.urls')),
    path('api/entity-recognition/', include('apps.entity_recognition.api.urls')),
    path('api/sentiment-analysis/', include('apps.sentiment_analysis.api.urls')),
    path('api/trend-analysis/', include('apps.trend_analysis.api.urls')),
    
    # Old app URLs (if they exist)
    path('api/accountss/', include('accountss.urls')),
    path('dashboard-stats/', get_dashboard_stats, name='dashboard_stats'),
    path('detailed-dashboard-stats/', get_detailed_dashboard_stats, name='detailed_dashboard_stats'),
    path('get_trend_by_sports_type/', get_trend_by_sports_type, name='detailed_dashboard_stats_by_sports_type'),
    
]