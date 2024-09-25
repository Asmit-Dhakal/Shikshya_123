
from django.db import models
from users.models import User
from course.models import Course
from django.conf import settings


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    comment = models.TextField()

    def __str__(self):
        return f'{self.course.title} review by {self.student.username}'

class Rating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    rating = models.PositiveIntegerField()  # Rating out of 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')

    def __str__(self):
        return f"Rating by {self.student.username} for {self.course.title}"
