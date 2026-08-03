# ecosystem/admin.py
from django.contrib import admin
from .models import Startup, Investor, Mentor, Competition, Achievement, Interaction

class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0
    fields = ('title', 'category', 'date', 'verified', 'nirf_countable')

class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    fk_name = 'startup'
    fields = ('actor', 'target', 'type', 'outcome')

class InteractionAsActorInline(admin.TabularInline):
    model = Interaction
    extra = 0
    fk_name = 'actor'
    fields = ('target', 'type', 'outcome', 'startup')

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ('startup_name', 'founder', 'sector', 'stage', 'trl')
    list_filter = ('sector', 'stage', 'is_active')
    search_fields = ('startup_name', 'pitch_summary', 'founder__full_name')
    inlines = [AchievementInline, InteractionInline]

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('firm_name', 'user', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('firm_name', 'mandate', 'user__full_name')

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_role', 'organization', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__full_name', 'current_role', 'organization')

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'organiser', 'event_date', 'nirf_recognised')
    list_filter = ('nirf_recognised',)
    search_fields = ('name', 'organiser')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'category', 'date', 'verified')
    list_filter = ('category', 'verified', 'nirf_countable')
    search_fields = ('title', 'profile__full_name')

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('actor', 'target', 'type', 'outcome', 'startup')
    list_filter = ('type', 'outcome')
    search_fields = ('actor__full_name', 'target__full_name', 'notes')