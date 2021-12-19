from django.contrib import admin

from .models import City, Profile, ProfileSearch, User

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(ProfileSearch)
admin.site.register(City)
