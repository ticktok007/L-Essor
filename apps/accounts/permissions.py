"""
apps/accounts/permissions.py
Campus Innovation & Engagement Intelligence Hub
Role-based DRF permission classes.
"""

from rest_framework.permissions import BasePermission


class BaseRolePermission(BasePermission):
    """
    Abstract base: subclasses set `allowed_role` to the required role string.
    Requires an authenticated user with a `role` attribute.
    """
    allowed_role: str = ""

    def has_permission(self, request, view) -> bool:
        return (
            request.user is not None
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == self.allowed_role
        )


class IsStudent(BaseRolePermission):
    """Grants access to users with role == 'student'."""
    allowed_role = "student"


class IsAlumni(BaseRolePermission):
    """Grants access to users with role == 'alumni'."""
    allowed_role = "alumni"


class IsInvestor(BaseRolePermission):
    """Grants access to users with role == 'investor'."""
    allowed_role = "investor"


class IsMentor(BaseRolePermission):
    """Grants access to users with role == 'mentor'."""
    allowed_role = "mentor"


class IsAdmin(BaseRolePermission):
    """
    Grants access to users with role == 'admin'.
    NOTE: maps to user.role, NOT to is_staff or is_superuser.
    Django Admin panel access is controlled separately via is_staff.
    """
    allowed_role = "admin"