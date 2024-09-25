from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_teacher', 'is_student', 'is_active', 'is_staff')
    list_filter = ('is_teacher', 'is_student', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address', 'country', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_teacher', 'is_student', 'address', 'country', 'phone_number'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)
