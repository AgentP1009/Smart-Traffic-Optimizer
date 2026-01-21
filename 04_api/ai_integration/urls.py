# ai_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('detect/', views.detect_vehicles, name='detect_vehicles'),
    path('optimize/', views.optimize_traffic, name='optimize_traffic'),  # NEW
    path('live/start/', views.start_live_detection, name='start_live_detection'),
    path('live/stop/', views.stop_live_detection, name='stop_live_detection'),
    path('live/stats/', views.get_live_stats, name='get_live_stats'),
    path('models/', views.ai_models, name='ai_models'),
]