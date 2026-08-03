# accounts/permissions.py
from rest_framework import permissions

class IsStudentSelf(permissions.BasePermission):
    """Object-level permission to only allow students to access their own profile."""
    def has_object_permission(self, request, view, obj):
        # Assumes obj is Profile and has a 'user' field
        return obj.user == request.user

class IsLeadership(permissions.BasePermission):
    """Allows access only to users with the leadership role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'leadership'

class IsStudentOrLeadership(permissions.BasePermission):
    """Allows access to students or leadership users."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['student', 'leadership']