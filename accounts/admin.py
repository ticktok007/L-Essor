# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Profile
from ecosystem.admin import AchievementInline, InteractionAsActorInline

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'full_name')

    @admin.display(description='Full Name', ordering='full_name')
    def get_full_name(self, obj):
        return obj.full_name

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Fix: Reference 'get_full_name' (the method below) instead of 'full_name'
    list_display = ('get_full_name', 'department', 'graduation_year', 'get_role')
    list_filter = ('department', 'graduation_year', 'user__role')
    search_fields = ('user__full_name', 'user__email', 'bio')
    inlines = [AchievementInline, InteractionAsActorInline]

    @admin.display(description='Full Name', ordering='user__full_name')
    def get_full_name(self, obj):
        return obj.user.full_name

    @admin.display(description='Role')
    def get_role(self, obj):
        return obj.user.role