# matching/test_data.py
import uuid
from accounts.models import User, Profile
from ecosystem.models import Startup, Investor
from matching.embeddings import encode

def create_test_investor(firm_name: str, mandate: str, sectors: list):
    user = User.objects.create_user(email=f"{uuid.uuid4().hex[:8]}@test.com", password="p", role="investor")
    return Investor.objects.create(
        user=user,
        firm_name=firm_name,
        mandate_text=mandate,
        mandate_embedding=encode(mandate),
        sectors=sectors
    )

def create_test_startup(founder: User, name: str, pitch: str, sector: str):
    return Startup.objects.create(
        founder=founder,
        startup_name=name,
        pitch_summary=pitch,
        pitch_embedding=encode(pitch),
        sector=sector
    )