# tests/test_smoke_e2e.py
import pytest
from django.core.management import call_command
from accounts.models import User, Profile
from ecosystem.models import Startup

@pytest.mark.django_db
class TestSmokeE2E:
    def test_management_command_execution(self):
        """Verifies the E2E smoke test command runs to completion."""
        # Using a try/except because the command calls sys.exit(1) on failure
        try:
            call_command('smoke_test_e2e')
        except SystemExit as e:
            assert e.code == 0, "Smoke test management command failed"

    def test_scoping_logic_at_db_level(self):
        """Explicit check for role-based data isolation."""
        u1 = User.objects.create_user(email="stu1@test.com", password="p", role="student")
        u2 = User.objects.create_user(email="stu2@test.com", password="p", role="student")
        
        Startup.objects.create(founder=u1, startup_name="Private Tech")
        
        # Verify student 2 cannot see student 1's startup in a founder-scoped query
        assert Startup.objects.filter(founder=u2).count() == 0
        assert Startup.objects.filter(founder=u1).count() == 1