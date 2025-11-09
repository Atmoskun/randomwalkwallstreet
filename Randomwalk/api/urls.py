from django.urls import path
from . import views

# This maps the root URL (yourwebsite.com/) to the 'quarterly_selection_view'

urlpatterns = [
    path('', views.quarterly_selection_view, name='quarterly_selection'),
]
