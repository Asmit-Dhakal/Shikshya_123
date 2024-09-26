from rest_framework import serializers

from Shikshya import settings
from .models import Review, Rating
from course.models import Course
from users.models import User  # Assuming User is your custom User model


class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')  # To show student's username in the response
    course_title = serializers.ReadOnlyField(source='course.title')  # To show course title in the response

    class Meta:
        model = Review
        fields = ['id', 'comment', 'course_title', 'student_name', 'student_name']
        read_only_fields = ['student', 'course']


class RatingSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')  # To show student's username in the response
    course_title = serializers.ReadOnlyField(source='course.title')  # To show course title in the response

    class Meta:
        model = Rating
        fields = ['id', 'rating', 'course_title', 'student_name', 'student_name', 'created_at']
        read_only_fields = ['student', 'course', 'created_at']



class CourseSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'teacher', 'title', 'description', 'thumbnail', 'thumbnail_url', 'validation_date', 'price']
        read_only_fields = ['teacher']

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return f"{settings.BASE_URL}{obj.thumbnail.url}"  # Static base URL as a fallback
        return ''

