from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


# Remove the UserProfileInline from the custom UserAdmin
class CustomUserAdmin(UserAdmin):
    pass


# Re-register the UserAdmin without the inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Keep UserProfile registered separately for direct editing
admin.site.register(UserProfile)
