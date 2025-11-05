from django.urls import path
from .views import health, analyze

urlpatterns = [
    path('health', health, name='health'),
    path('analyze', analyze, name='analyze'),
]

