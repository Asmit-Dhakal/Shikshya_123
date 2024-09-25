from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Review, Course
from .serializers import ReviewSerializer, CourseSerializer
from .utils import get_recommendations_for_user


class ReviewListCreate(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class RecommendationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        num_recommendations = request.query_params.get('num_recommendations', 5)  # Default to 5 if not provided

        # Ensure num_recommendations is an integer
        try:
            num_recommendations = int(num_recommendations)
        except ValueError:
            num_recommendations = 5  # Fallback to default if conversion fails

        recommended_course_ids = get_recommendations_for_user(user_id, num_recommendations=num_recommendations)

        # Fetch detailed information for the recommended courses
        recommended_courses = Course.objects.filter(id__in=recommended_course_ids)
        serializer = CourseSerializer(recommended_courses, many=True)

        return Response({'recommended_courses': serializer.data}, status=status.HTTP_200_OK)
