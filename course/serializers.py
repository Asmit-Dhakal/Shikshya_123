from rest_framework import serializers
from .models import Course, Booking, Payment, Chapter, Video
from profiles.models import TeacherProfile  # Assuming TeacherProfile is another app's model
from users.models import User  # Assuming User is your custom User model


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
            return f"https://192.168.18.237:8003{obj.thumbnail.url}"  # Provide a static base URL for the thumbnail
        return ''


class VideoSerializer(serializers.ModelSerializer):
    full_video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'video_file', 'upload_date', 'full_video_url']

    def get_full_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_file:
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return f"https://192.168.18.237:8003{obj.video_file.url}"  # Provide a static base URL for the video file
        return ''


class ChapterSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'videos']


class CourseDetailSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'teacher', 'title', 'description', 'thumbnail', 'thumbnail_url', 'validation_date', 'price', 'chapters']
        read_only_fields = ['teacher']

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return f"https://192.168.18.237:8003{obj.thumbnail.url}"  # Provide a static base URL for the thumbnail
        return ''


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['transaction_id', 'amount', 'status']


class BookingSerializer(serializers.ModelSerializer):
    payment_info = PaymentSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'student', 'course', 'booked_on', 'payment_info']
        read_only_fields = ['student', 'booked_on']


class TeacherProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ['bio', 'expertise']


class TeacherDashboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    address = serializers.CharField()
    country = serializers.CharField()
    phone_number = serializers.CharField()
    bio = serializers.SerializerMethodField()
    expertise = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'address', 'country', 'phone_number',
            'bio', 'expertise', 'courses', 'bookings', 'payments'
        ]

    def get_bio(self, obj):
        try:
            profile = TeacherProfile.objects.get(teacher=obj)
            return profile.bio or "No bio available"
        except TeacherProfile.DoesNotExist:
            return "No bio available"

    def get_expertise(self, obj):
        try:
            profile = TeacherProfile.objects.get(teacher=obj)
            return profile.expertise or "No expertise provided"
        except TeacherProfile.DoesNotExist:
            return "No expertise provided"

    # Use CourseDetailSerializer to include chapters and videos
    def get_courses(self, obj):
        courses = Course.objects.filter(teacher=obj)
        return CourseDetailSerializer(courses, many=True, context=self.context).data if courses.exists() else []

    def get_bookings(self, obj):
        bookings = Booking.objects.filter(course__teacher=obj)
        return BookingSerializer(bookings, many=True, context=self.context).data if bookings.exists() else []

    def get_payments(self, obj):
        payments = Payment.objects.filter(course__teacher=obj)
        return PaymentSerializer(payments, many=True).data if payments.exists() else []

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.address = validated_data.get('address', instance.address)
        instance.country = validated_data.get('country', instance.country)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        profile_data = validated_data.get('profile', {})
        profile, created = TeacherProfile.objects.get_or_create(teacher=instance)
        profile.bio = profile_data.get('bio', profile.bio)
        profile.expertise = profile_data.get('expertise', profile.expertise)
        profile.save()

        return instance
