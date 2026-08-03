# dashboard/services.py
from django.db.models import Count, Q
from accounts.models import Profile, User
from ecosystem.models import Startup, Achievement

def build_student_dashboard(user):
    profile = user.profile
    achievements = Achievement.objects.filter(profile=profile)
    startups = Startup.objects.filter(founder=user)
    
    return {
        "profile": profile,
        "achievements_count": achievements.count(),
        "startups_count": startups.count(),
        "recent_achievements": achievements.order_by('-created_at')[:5].values('id', 'title', 'category', 'date')
    }

def build_leadership_dashboard():
    profiles = Profile.objects.all()
    # Department distribution
    dept_stats = profiles.values('department').annotate(count=Count('department'))
    dept_counts = {item['department']: item['count'] for item in dept_stats if item['department']}

    return {
        "total_profiles": profiles.count(),
        "total_students": User.objects.filter(role='student').count(),
        "total_startups": Startup.objects.count(),
        "total_achievements": Achievement.objects.count(),
        "at_risk_students": profiles.filter(at_risk_flag=True).count(),
        "department_counts": dept_counts,
        "recent_startups": Startup.objects.order_by('-created_at')[:5].values('id', 'startup_name', 'sector', 'stage')
    }