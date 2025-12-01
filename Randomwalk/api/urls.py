from django.urls import path
from . import views

urlpatterns = [
    # Main page view (default path for the app)
    path('', views.quarterly_selection_view, name='quarterly_selection'),

    # Analytics / Tracking endpoint
    path('tracking/api/update-time/', views.update_visit_time, name='update_time'),
]
