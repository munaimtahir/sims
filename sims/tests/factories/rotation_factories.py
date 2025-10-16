<<<<<<< HEAD
"""Factories for Rotation models"""
import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from datetime import date, timedelta
from sims.rotations.models import Hospital, Department, Rotation, RotationEvaluation
from .user_factories import PGFactory, SupervisorFactory
=======
"""Factories for Rotations models"""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from sims.rotations.models import Hospital, Department, Rotation
from .user_factories import SupervisorFactory, PGFactory
>>>>>>> origin/main


class HospitalFactory(DjangoModelFactory):
    """Factory for Hospital model."""

    class Meta:
        model = Hospital

    name = factory.Sequence(lambda n: f"Hospital {n}")
<<<<<<< HEAD
    code = factory.Sequence(lambda n: f"HOSP{n:03d}")
    address = factory.Faker("address")
    phone = factory.Faker("phone_number")
    email = factory.Faker("email")
    website = factory.Faker("url")
    description = factory.Faker("paragraph")
    facilities = factory.Faker("paragraph")
=======
    address = factory.Faker("address")
    phone = factory.Faker("phone_number")
>>>>>>> origin/main
    is_active = True


class DepartmentFactory(DjangoModelFactory):
    """Factory for Department model."""

    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Department {n}")
    hospital = factory.SubFactory(HospitalFactory)
    head_of_department = factory.Faker("name")
<<<<<<< HEAD
    contact_email = factory.Faker("email")
    contact_phone = factory.Faker("phone_number")
    description = factory.Faker("paragraph")
    is_active = True


class RotationFactory(DjangoModelFactory):
    """Factory for Rotation model with all required fields."""
=======


class RotationFactory(DjangoModelFactory):
    """Factory for Rotation model."""
>>>>>>> origin/main

    class Meta:
        model = Rotation

    pg = factory.SubFactory(PGFactory)
    supervisor = factory.LazyAttribute(lambda obj: obj.pg.supervisor)
<<<<<<< HEAD
    name = factory.Sequence(lambda n: f"Rotation {n}")
    department = factory.SubFactory(DepartmentFactory)
    hospital = factory.LazyAttribute(lambda obj: obj.department.hospital)
    specialty = "medicine"
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=60))
    duration_weeks = 12
    objectives = factory.Faker("paragraph")
    expected_competencies = factory.Faker("paragraph")
    status = "ongoing"
    is_active = True


class RotationEvaluationFactory(DjangoModelFactory):
    """Factory for RotationEvaluation model."""

    class Meta:
        model = RotationEvaluation

    rotation = factory.SubFactory(RotationFactory)
    evaluator = factory.LazyAttribute(lambda obj: obj.rotation.supervisor)
    clinical_knowledge_score = 4
    clinical_skills_score = 4
    professionalism_score = 5
    communication_score = 4
    teamwork_score = 5
    overall_score = 4
    strengths = factory.Faker("paragraph")
    areas_for_improvement = factory.Faker("paragraph")
    comments = factory.Faker("paragraph")
    status = "submitted"
=======
    hospital = factory.SubFactory(HospitalFactory)
    department = factory.SubFactory(DepartmentFactory)
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=60))
    status = "active"
>>>>>>> origin/main
