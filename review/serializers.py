from rest_framework import serializers
from .models import Review
from course.models import Course
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'teacher', 'title', 'description', 'thumbnail','validation_date', 'price']
        read_only_fields = [ 'teacher']
