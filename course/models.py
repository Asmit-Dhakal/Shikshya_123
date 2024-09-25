from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.shortcuts import reverse

class Course(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True}
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    validation_date = models.DateField()
    thumbnail = models.FileField(upload_to='thumbnail_photo/', null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title

    def image_url(self):
        """Returns the absolute URL for the thumbnail image."""
        if self.thumbnail:
            return self.thumbnail.url  # Relative URL for local access
        return ''

    def full_image_url(self):
        if self.thumbnail:
            return f"https://192.168.18.237:8003{self.thumbnail.url}"  # Replace 127.0.0.1 with your IP if needed
        return ''


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Video(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='course_videos/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

    def video_url(self):
        """Returns the relative URL for the video file."""
        if self.video_file:
            return self.video_file.url  # Local access URL
        return ''


    def full_video_url(self):
       if self.video_file:
        return f"https://192.168.18.237:8003{self.video_file.url}"  # Replace 127.0.0.1 with your IP if needed
       return ''


class Booking(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='bookings')
    booked_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} booked {self.course.title}"

class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('khalti', 'Khalti'),
        ('esewa', 'eSewa'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    payment_gateway = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='esewa')
    transaction_id = models.CharField(max_length=100, unique=True)
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.transaction_id}"