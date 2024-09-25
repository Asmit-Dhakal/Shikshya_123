from django.urls import path
from .views import RegisterView, LoginView, StudentDashboardView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # Unified registration path
    path('login/', LoginView.as_view(), name='login'),           # Unified login path
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('student-dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),
]
