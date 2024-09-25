from django.contrib import admin

# Register your models here.
from django.contrib import admin

from review.models import Review, Rating


# Register your models here.
admin.site.register(Review)
admin.site.register(Rating)