"""Factories for Certificates models"""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from sims.certificates.models import CertificateType, Certificate
from .user_factories import PGFactory


class CertificateTypeFactory(DjangoModelFactory):
    """Factory for CertificateType model."""

    class Meta:
        model = CertificateType

    name = factory.Sequence(lambda n: f"Certificate Type {n}")
    description = factory.Faker("paragraph")
    is_active = True


class CertificateFactory(DjangoModelFactory):
    """Factory for Certificate model."""

    class Meta:
        model = Certificate

    pg = factory.SubFactory(PGFactory)
    certificate_type = factory.SubFactory(CertificateTypeFactory)
    title = factory.Faker("sentence", nb_words=6)
    issue_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    expiry_date = factory.LazyFunction(lambda: date.today() + timedelta(days=365))
    issuing_organization = factory.Faker("company")
    status = "active"
    is_active = True
