from django.urls import path
from .views import (
    CourseCreateView, CourseListView, CourseDetailView,
    ChapterCreateView, ChapterListView,
    VideoCreateView, VideoListView, VideoStreamView,
    BookCourseView, BookedCoursesView, BookingDetailView, DeleteBookingView,
    PaymentCreateView, EsewaPaymentInitiationView, EsewaPaymentSuccessView, TeacherDashboardView
)

urlpatterns = [
    # Course management
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course_create'),

    # Chapter management
    path('courses/<int:course_id>/chapters/', ChapterListView.as_view(), name='chapter_list'),
    path('courses/<int:course_id>/chapters/create/', ChapterCreateView.as_view(), name='chapter_create'),

    # Video management
    path('chapters/<int:chapter_id>/videos/', VideoListView.as_view(), name='video_list'),
    path('chapters/<int:chapter_id>/videos/create/', VideoCreateView.as_view(), name='video_create'),
    path('videos/<int:video_id>/stream/', VideoStreamView.as_view(), name='video_stream'),

    # Booking management
    path('courses/<int:course_id>/book/', BookCourseView.as_view(), name='course_book'),
    path('courses/booked/', BookedCoursesView.as_view(), name='booked_courses'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/delete/<int:course_id>/', DeleteBookingView.as_view(), name='delete_booking'),

    # Payment management
    path('payments/esewa/initiate/', EsewaPaymentInitiationView.as_view(), name='esewa_payment_initiate'),
    path('payments/esewa/success/', EsewaPaymentSuccessView.as_view(), name='esewa_payment_success'),


   path('teacher-dashboard/',TeacherDashboardView.as_view(), name='teacher_dashboard'),
]
