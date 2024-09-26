from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Avg
from .models import Review, Course, Rating
from .serializers import ReviewSerializer, CourseSerializer, RatingSerializer
from .utils import get_recommendations_for_user



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


class ReviewListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        """
        Handle GET requests to list all reviews for a specific course.
        """
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(course=course)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_id):
        """
        Handle POST requests to create a new review for a course.
        Automatically assign the logged-in user as the student.
        """
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        student = request.user

        # Check if the user has already posted a review for this course
        if Review.objects.filter(course=course, student=student).exists():
            return Response({"error": "You have already posted a review for this course."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student, course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Avg
from .models import Rating
from course.models import Course
from .serializers import RatingSerializer

class RatingListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, course_id):
        """
        Handle GET requests to return the average rating of a specific course.
        """
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        ratings = Rating.objects.filter(course=course)
        if ratings.exists():
            # Calculate the average rating
            average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            return Response({"average_rating": average_rating}, status=status.HTTP_200_OK)
        return Response({"message": "No ratings available for this course."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id):
        """
        Handle POST requests to create a new rating for a course.
        Automatically assign the logged-in user as the student.
        """
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        student = request.user

        # Check if the user has already rated this course
        if Rating.objects.filter(course=course, student=student).exists():
            return Response({"error": "You have already rated this course."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student, course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
