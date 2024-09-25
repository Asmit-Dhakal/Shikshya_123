from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from users.models import User  # Import the User model
from profiles.models import TeacherProfile
from profiles.serializers import UserSerializer, TeacherProfileSerializer
from .models import Course, Booking, Chapter, Video, Payment
from .serializers import CourseSerializer, BookingSerializer, ChapterSerializer, VideoSerializer, PaymentSerializer, \
    CourseDetailSerializer, TeacherDashboardSerializer
import os
from django.http import StreamingHttpResponse, Http404
import re
import requests


# Helper function to serve video files with byte-range support
def open_file(request, path, chunk_size=8192):
    file_size = os.path.getsize(path)
    range_header = request.headers.get('Range', '').strip()
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    content_type = 'video/mp4'

    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte)
        last_byte = int(last_byte) if last_byte else file_size - 1
        length = last_byte - first_byte + 1
        response = StreamingHttpResponse(file_chunk(path, first_byte, length), status=206, content_type=content_type)
        response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
    else:
        response = StreamingHttpResponse(file_chunk(path), content_type=content_type)

    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = file_size
    return response


def file_chunk(path, start=0, length=None, chunk_size=8192):
    with open(path, 'rb') as f:
        f.seek(start)
        while length is None or length > 0:
            chunk = f.read(chunk_size if length is None else min(chunk_size, length))
            if not chunk:
                break
            yield chunk
            if length:
                length -= len(chunk)


# ----------------------------------------
# Course Management
# ----------------------------------------

class CourseListView(APIView):
    def get(self, request, *args, **kwargs):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Course, pk=pk)

    def get(self, request, pk, *args, **kwargs):
        course = self.get_object(pk)
        serializer = CourseDetailSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        course = self.get_object(pk)
        if request.user != course.teacher:
            raise PermissionDenied("Only the teacher who created the course can update it.")
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        course = self.get_object(pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CourseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied("Only teachers can create courses.")
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------
# Chapter Management
# ----------------------------------------

class ChapterCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)
        if request.user != course.teacher:
            raise PermissionDenied("Only the teacher who created the course can add chapters.")
        serializer = ChapterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChapterListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)
        chapters = Chapter.objects.filter(course=course)
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)


# ----------------------------------------
# Video Management with Payment Check
# ----------------------------------------

class VideoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chapter_id, *args, **kwargs):
        chapter = get_object_or_404(Chapter, id=chapter_id)
        if request.user != chapter.course.teacher:
            raise PermissionDenied("Only the teacher who created the course can add videos.")
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chapter=chapter)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chapter_id, *args, **kwargs):
        chapter = get_object_or_404(Chapter, id=chapter_id)
        videos = Video.objects.filter(chapter=chapter)
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)


# ----------------------------------------
# Video Streaming with Byte-Range Support
# ----------------------------------------

class VideoStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, video_id, *args, **kwargs):
        # Get the video object
        video = get_object_or_404(Video, id=video_id)
        course = video.chapter.course

        # Check if the user has completed payment for the course
        payment = Payment.objects.filter(student=request.user, course=course, status='completed').first()
        if not payment:
            raise PermissionDenied("You must complete the payment to access this video.")

        # Get the video file path
        video_path = video.video_file.path
        if not os.path.exists(video_path):
            raise Http404("Video not found.")

        # Stream the video file with byte-range support
        return open_file(request, video_path)


# ----------------------------------------
# Booking Management
# ----------------------------------------

class BookCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = get_object_or_404(Course, id=course_id)

        if Booking.objects.filter(student=request.user, course=course).exists():
            return Response({'detail': 'Already booked for this course.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create booking
        booking = Booking.objects.create(student=request.user, course=course)

        # Initiate payment process (you could also redirect to a payment gateway here)
        payment_data = {
            'student': request.user,
            'course': course,
            'amount': course.price,
            'status': 'pending',
            'transaction_id': 'temp_transaction_id',  # Replace with actual transaction ID
        }

        # Create payment
        payment = Payment.objects.create(**payment_data)

        return Response({
            'booking': BookingSerializer(booking).data,
            'payment': {
                'amount': payment.amount,
                'status': payment.status,
                'transaction_id': payment.transaction_id
            }
        }, status=status.HTTP_201_CREATED)


class BookedCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.filter(student=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Booking, pk=pk, student=self.request.user)

    def get(self, request, pk, *args, **kwargs):
        booking = self.get_object(pk)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)


class DeleteBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, course_id, *args, **kwargs):
        try:
            booking = Booking.objects.get(student=request.user, course_id=course_id)
            booking.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Booking.DoesNotExist:
            raise Http404("Booking not found.")


# ----------------------------------------
# Payment Management
# ----------------------------------------

class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get('transaction_id')
        payment = get_object_or_404(Payment, transaction_id=transaction_id)

        # Here you would validate the payment with your payment gateway
        # Assuming the payment is confirmed:
        payment.status = 'completed'  # Update status based on the payment gateway response
        payment.save()

        return Response({'detail': 'Payment completed successfully.'}, status=status.HTTP_200_OK)

# ----------------------------------------
# eSewa and  Payment Integration
# ----------------------------------------

class EsewaPaymentInitiationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        # Generate a unique transaction ID
        transaction_id = request.data.get('transaction_id')

        # Create a Payment entry in your database
        payment = Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            payment_gateway='esewa',
            transaction_id=transaction_id,
            status='pending'
        )

        # Prepare the eSewa payment initiation data
        esewa_merchant_code = "YOUR_ESEWA_MERCHANT_CODE"
        success_url = request.build_absolute_uri('/payments/esewa/success/')
        failure_url = request.build_absolute_uri('/payments/esewa/failure/')

        esewa_payment_url = f"https://uat.esewa.com.np/epay/main?amt={course.price}&pid={transaction_id}&scd={esewa_merchant_code}&su={success_url}&fu={failure_url}"

        # Return the payment URL
        return Response({'payment_url': esewa_payment_url}, status=status.HTTP_200_OK)


class EsewaPaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        amt = request.GET.get('amt')
        pid = request.GET.get('pid')
        refId = request.GET.get('refId')
        scd = "YOUR_ESEWA_MERCHANT_CODE"

        # Verify the payment with eSewa's API
        verification_url = f"https://uat.esewa.com.np/epay/transrec?amt={amt}&scd={scd}&pid={pid}&rid={refId}"
        response = requests.post(verification_url)

        if "Success" in response.text:
            payment = get_object_or_404(Payment, transaction_id=pid)
            payment.status = 'completed'
            payment.ref_id = refId
            payment.save()

            return Response({"detail": "Payment successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)


class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the user is a teacher
        if not request.user.is_teacher:
            return Response({"detail": "Only teachers can access the dashboard."}, status=status.HTTP_403_FORBIDDEN)

        # Fetch teacher profile details (handle missing profile gracefully)
        try:
            profile = TeacherProfile.objects.get(teacher=request.user)
            profile_serializer = TeacherProfileSerializer(profile)
        except TeacherProfile.DoesNotExist:
            profile_serializer = None

        # Fetch teacher's courses
        courses = Course.objects.filter(teacher=request.user)
        courses_serializer = CourseSerializer(courses, many=True)

        # Fetch payments related to teacher's courses
        payments = Payment.objects.filter(course__teacher=request.user)
        payments_serializer = PaymentSerializer(payments, many=True)

        # Combine all data into one response
        return Response({
            'profile': {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'address': request.user.address,
                'country': request.user.country,
                'phone_number': request.user.phone_number,
                'bio': profile_serializer.data['bio'] if profile_serializer else "No bio available",
                'expertise': profile_serializer.data['expertise'] if profile_serializer else "No expertise available"
            },
            'courses': courses_serializer.data if courses else [],
            'payments': payments_serializer.data if payments else [],
        }, status=status.HTTP_200_OK)




def dashboard(request):
    return render(request, 'course/teacher_dashboard.html')


