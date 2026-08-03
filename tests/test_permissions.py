# tests/test_permissions.py
import pytest
from unittest.mock import Mock
from accounts.permissions import IsStudentSelf, IsLeadership

def test_is_leadership_allow():
    perm = IsLeadership()
    request = Mock(user=Mock(is_authenticated=True, role="leadership"))
    assert perm.has_permission(request, None) is True

def test_is_leadership_deny():
    perm = IsLeadership()
    request = Mock(user=Mock(is_authenticated=True, role="student"))
    assert perm.has_permission(request, None) is False

def test_is_student_self_obj_allow():
    perm = IsStudentSelf()
    user = Mock()
    request = Mock(user=user)
    obj = Mock(user=user)
    assert perm.has_object_permission(request, None, obj) is True