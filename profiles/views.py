from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StudentProfile, TeacherProfile
from .serializers import StudentProfileSerializer, TeacherProfileSerializer, ChangePasswordSerializer, UserSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self):
        """Return the correct profile based on whether the user is a student or teacher."""
        if self.request.user.is_teacher:
            # Use filter and first to prevent throwing an exception if the profile doesn't exist
            return TeacherProfile.objects.filter(teacher=self.request.user).first(), 'teacher'

        if self.request.user.is_student:
            return StudentProfile.objects.filter(student=self.request.user).first(), 'student'

        return None, None  # If the user is neither a student nor a teacher

    def get(self, request, *args, **kwargs):
        profile, role = self.get_profile()

        # Serialize the user data
        user_serializer = UserSerializer(request.user)
        response_data = user_serializer.data

        # Add student or teacher profile to response data if it exists
        if role == 'student' and profile:
            response_data['student_profile'] = {
                'additional_info': profile.additional_info
            }
        elif role == 'teacher' and profile:
            response_data['teacher_profile'] = {
                'expertise': profile.expertise,
                'bio': profile.bio
            }

        # Return user data along with profile data if available
        return Response(response_data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Save basic user fields
            serializer.save()

            # Handle profile creation or update
            if user.is_student:
                student_profile, created = StudentProfile.objects.get_or_create(student=user)
                if 'student_profile' in request.data:
                    student_profile_data = request.data.get('student_profile', {})
                    student_profile.additional_info = student_profile_data.get('additional_info', student_profile.additional_info)
                    student_profile.save()

            if user.is_teacher:
                teacher_profile, created = TeacherProfile.objects.get_or_create(teacher=user)
                if 'teacher_profile' in request.data:
                    teacher_profile_data = request.data.get('teacher_profile', {})
                    teacher_profile.expertise = teacher_profile_data.get('expertise', teacher_profile.expertise)
                    teacher_profile.bio = teacher_profile_data.get('bio', teacher_profile.bio)
                    teacher_profile.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()  # Save the new password
            return Response({"detail": "Password has been changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


