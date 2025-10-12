"""Factories for Logbook models"""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from sims.logbook.models import Diagnosis, Procedure, LogbookEntry
from .user_factories import SupervisorFactory, PGFactory


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
    """Factory for LogbookEntry model."""

    class Meta:
        model = LogbookEntry

    pg = factory.SubFactory(PGFactory)
    supervisor = factory.LazyAttribute(lambda obj: obj.pg.supervisor)
    case_title = factory.Faker("sentence", nb_words=6)
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=7))
    location_of_activity = factory.Faker("city")
    patient_history_summary = factory.Faker("paragraph")
    management_action = factory.Faker("paragraph")
    topic_subtopic = factory.Faker("sentence", nb_words=4)
    patient_age = 45
    patient_gender = "M"
    status = "draft"
    is_active = True

