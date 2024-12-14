from django.contrib import admin

from .models import Collection, UserProfile

# No custom UserAdmin registration, so remove:
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

admin.site.register(Collection)
admin.site.register(UserProfile)
