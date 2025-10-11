"""Factories for Rotations models"""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from sims.rotations.models import Hospital, Rotation
from .user_factories import SupervisorFactory, PGFactory


class HospitalFactory(DjangoModelFactory):
    """Factory for Hospital model."""

    class Meta:
        model = Hospital

    name = factory.Sequence(lambda n: f"Hospital {n}")
    location = factory.Faker("city")
    is_active = True


class RotationFactory(DjangoModelFactory):
    """Factory for Rotation model."""

    class Meta:
        model = Rotation

    pg = factory.SubFactory(PGFactory)
    supervisor = factory.LazyAttribute(lambda obj: obj.pg.supervisor)
    hospital = factory.SubFactory(HospitalFactory)
    specialty = "medicine"
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=60))
    status = "active"
    is_active = True
