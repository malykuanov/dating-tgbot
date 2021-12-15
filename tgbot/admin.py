from django.contrib import admin

from .models import City, Profile, User

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(City)
