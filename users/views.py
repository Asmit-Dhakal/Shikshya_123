from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, serializers
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from .serializers import TeacherRegisterSerializer, StudentRegisterSerializer
from rest_framework.permissions import IsAuthenticated


# Unified Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        # Determine the serializer based on the requested role
        role = self.request.data.get('role')
        if role == 'teacher':
            return TeacherRegisterSerializer
        elif role == 'student':
            return StudentRegisterSerializer
        return None

    def create(self, request, *args, **kwargs):
        role = request.data.get('role')
        serializer_class = self.get_serializer_class()

        if not serializer_class:
            return Response({'message': 'Invalid role specified.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': f'{role.capitalize()} registration successful',
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            errors = e.detail
            return Response({
                'message': 'Validation failed',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Unified Login View
class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        role = 'teacher' if user.is_teacher else 'student' if user.is_student else 'unknown'
        if role == 'unknown':
            return Response({'detail': 'Role not recognized.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': role
        })

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_student:
            return Response({'detail': 'Student access required.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'message': 'Welcome to the Student Dashboard!'}, status=status.HTTP_200_OK)

def login(request):

    return render(request, 'course/login.html')
