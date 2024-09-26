from rest_framework import serializers

from Shikshya import settings
from .models import Review
from course.models import Course


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

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

