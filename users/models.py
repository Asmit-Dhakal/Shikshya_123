from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email'),
            models.UniqueConstraint(fields=['username'], name='unique_username')
        ]

    def __str__(self):
        return self.username
