from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'address', 'country', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            address=validated_data.get('address', ''),
            country=validated_data.get('country', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user

class TeacherRegisterSerializer(UserSerializer):
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_teacher=True,
            address=validated_data.get('address', ''),
            country=validated_data.get('country', ''),
            phone_number=validated_data.get('phone_number', '')
        )

class StudentRegisterSerializer(UserSerializer):
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_student=True,
            address=validated_data.get('address', ''),
            country=validated_data.get('country', ''),
            phone_number=validated_data.get('phone_number', '')
        )
