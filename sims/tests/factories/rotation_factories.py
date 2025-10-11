"""Factories for Rotations models"""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from sims.rotations.models import Hospital, Department, Rotation
from .user_factories import SupervisorFactory, PGFactory


class HospitalFactory(DjangoModelFactory):
    """Factory for Hospital model."""

    class Meta:
        model = Hospital

    name = factory.Sequence(lambda n: f"Hospital {n}")
    address = factory.Faker("address")
    phone = factory.Faker("phone_number")
    is_active = True


class DepartmentFactory(DjangoModelFactory):
    """Factory for Department model."""

    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Department {n}")
    hospital = factory.SubFactory(HospitalFactory)
    head_of_department = factory.Faker("name")


class RotationFactory(DjangoModelFactory):
    """Factory for Rotation model."""

    class Meta:
        model = Rotation

    pg = factory.SubFactory(PGFactory)
    supervisor = factory.LazyAttribute(lambda obj: obj.pg.supervisor)
    hospital = factory.SubFactory(HospitalFactory)
    department = factory.SubFactory(DepartmentFactory)
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=60))
    status = "active"
