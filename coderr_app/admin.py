from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at')  # Angezeigte Felder in der Admin-Liste
    search_fields = ('user__username', 'type')     # Suchfelder im Admin
admin.site.register(UserProfile, UserProfileAdmin)