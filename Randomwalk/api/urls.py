from django.urls import path
from . import views

urlpatterns = [
    # 1. This is the path for your webpage (the homepage)
    path('', views.quarterly_selection_view, name='quarterly_selection'),
    
    # 2. Add the path for the 'health' function
    path('api/health', views.health, name='api_health'),
    
    # 3. Add the path for the 'analyze' function
    path('api/analyze', views.analyze, name='api_analyze'),
]
