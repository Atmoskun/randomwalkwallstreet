from django.urls import path
from . import views

urlpatterns = [
    # Main page view (default path for the app)
    path('', views.quarterly_selection_view, name='quarterly_selection'),
    
    # Health check for deployment monitoring - now just '/health'
    path('health', views.health, name='api_health'),
    
    # Analysis API endpoint - now just '/analyze'
    path('analyze', views.analyze, name='analyze_data'), 
]
