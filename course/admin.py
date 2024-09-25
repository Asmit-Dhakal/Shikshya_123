from django.contrib import admin

from course.models import Course , Booking , Video, Chapter

# Register your models here.
admin.site.register(Course)
admin.site.register(Booking)
admin.site.register(Video)
admin.site.register(Chapter)