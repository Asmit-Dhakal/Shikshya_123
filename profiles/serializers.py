from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import StudentProfile, TeacherProfile

User = get_user_model()

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['additional_info']

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ['expertise', 'bio']

class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    teacher_profile = TeacherProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=False)  # For password changes

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'address',
            'country', 'teacher_profile', 'student_profile', 'password'
        ]
        read_only_fields = ['username', 'email', 'id']  # Prevent changes to username and email

    def update(self, instance, validated_data):
        # Update user fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.country = validated_data.get('country', instance.country)

        # Check if password change is requested and validate it
        password = validated_data.get('password', None)
        if password:
            validate_password(password, instance)
            instance.set_password(password)

        instance.save()

        # Handle student profile update or creation
        if instance.is_student and 'student_profile' in validated_data:
            student_profile_data = validated_data.pop('student_profile')
            student_profile, created = StudentProfile.objects.get_or_create(student=instance)
            student_profile.additional_info = student_profile_data.get('additional_info', student_profile.additional_info)
            student_profile.save()

        # Handle teacher profile update or creation
        if instance.is_teacher and 'teacher_profile' in validated_data:
            teacher_profile_data = validated_data.pop('teacher_profile')
            teacher_profile, created = TeacherProfile.objects.get_or_create(teacher=instance)
            teacher_profile.expertise = teacher_profile_data.get('expertise', teacher_profile.expertise)
            teacher_profile.bio = teacher_profile_data.get('bio', teacher_profile.bio)
            teacher_profile.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError("The new passwords do not match.")

        # Validate the new password strength
        validate_password(new_password)

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
