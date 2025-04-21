import pytest
from django.urls import reverse
from .models import Cottage

pytestmark = pytest.mark.django_db

def test_str():
    obj = Cottage.objects.create(
        name="Aurora Hut",
        description="Glass‑roof igloo in Lapland",
        location="Saariselkä",
        beds=2,
        base_price=180,
    )
    assert str(obj) == "Aurora Hut"