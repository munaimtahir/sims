"""Factories for Logbook models"""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
<<<<<<< HEAD
from sims.logbook.models import Diagnosis, Procedure, LogbookEntry, LogbookReview
from .user_factories import PGFactory, SupervisorFactory
=======
from sims.logbook.models import Diagnosis, Procedure, LogbookEntry
from .user_factories import SupervisorFactory, PGFactory
>>>>>>> origin/main


class DiagnosisFactory(DjangoModelFactory):
    """Factory for Diagnosis model."""

    class Meta:
        model = Diagnosis

    name = factory.Sequence(lambda n: f"Diagnosis {n}")
    category = "other"
    is_active = True


class ProcedureFactory(DjangoModelFactory):
    """Factory for Procedure model."""

    class Meta:
        model = Procedure

    name = factory.Sequence(lambda n: f"Procedure {n}")
    category = "diagnostic"
    is_active = True


class LogbookEntryFactory(DjangoModelFactory):
<<<<<<< HEAD
    """Factory for LogbookEntry model with all required fields."""
=======
    """Factory for LogbookEntry model."""
>>>>>>> origin/main

    class Meta:
        model = LogbookEntry

    pg = factory.SubFactory(PGFactory)
    supervisor = factory.LazyAttribute(lambda obj: obj.pg.supervisor)
    case_title = factory.Faker("sentence", nb_words=6)
<<<<<<< HEAD
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=5))
    location_of_activity = factory.Faker("city")
    patient_history_summary = factory.Faker("paragraph")
    management_action = factory.Faker("paragraph")
    topic_subtopic = factory.Faker("word")
    patient_age = 45
    patient_gender = "M"
    patient_chief_complaint = factory.Faker("sentence")
    primary_diagnosis = factory.SubFactory(DiagnosisFactory)
    clinical_reasoning = factory.Faker("paragraph")
    learning_points = factory.Faker("paragraph")
    status = "draft"


class LogbookReviewFactory(DjangoModelFactory):
    """Factory for LogbookReview model."""

    class Meta:
        model = LogbookReview

    entry = factory.SubFactory(LogbookEntryFactory)
    reviewer = factory.LazyAttribute(lambda obj: obj.entry.supervisor)
    rating = 4
    feedback = factory.Faker("paragraph")
    recommendations = factory.Faker("paragraph")
    status = "approved"
=======
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=7))
    location_of_activity = factory.Faker("city")
    patient_history_summary = factory.Faker("paragraph")
    management_action = factory.Faker("paragraph")
    topic_subtopic = factory.Faker("sentence", nb_words=4)
    patient_age = 45
    patient_gender = "M"
    status = "draft"
    is_active = True
>>>>>>> origin/main
