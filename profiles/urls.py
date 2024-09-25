from django.urls import path
from .views import UserProfileView, ChangePasswordView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),  # Handles GET and PATCH for profile
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),  # Handles POST for password change
]
