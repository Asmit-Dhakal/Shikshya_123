from django.urls import path
from .views import RecommendationView, ReviewListCreateView, RatingListCreateView



urlpatterns = [
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('reviews/<int:course_id>/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('ratings/<int:course_id>/', RatingListCreateView.as_view(), name='rating-list-create'),
]
