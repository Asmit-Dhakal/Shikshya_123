from django.urls import path
from .views import RecommendationView

urlpatterns = [
    # Other URL patterns
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
]
