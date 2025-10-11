from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from .models import CaseCategory, ClinicalCase, CaseReview, CaseStatistics
from .forms import ClinicalCaseForm, CaseReviewForm
from sims.tests.factories.user_factories import AdminFactory, SupervisorFactory, PGFactory
from sims.tests.factories.logbook_factories import DiagnosisFactory
from sims.tests.factories.case_factories import ClinicalCaseFactory, CaseCategoryFactory

User = get_user_model()


class CaseCategoryModelTest(TestCase):
    """Test the CaseCategory model"""

    def setUp(self):
        self.category = CaseCategory.objects.create(
            name="Cardiology", description="Heart and cardiovascular cases", color_code="#FF5722"
        )

    def test_category_creation(self):
        """Test category creation and string representation"""
        self.assertEqual(str(self.category), "Cardiology")
        self.assertEqual(self.category.color_code, "#FF5722")
        self.assertTrue(self.category.is_active)

    def test_category_validation(self):
        """Test category field validation"""
        # Test color code validation
        category = CaseCategory(name="Test Category", color_code="invalid_color")
        with self.assertRaises(Exception):
            category.full_clean()


class ClinicalCaseModelTest(TestCase):
    """Test the ClinicalCase model"""

    def setUp(self):
        # Create test users and case using factories
        self.supervisor = SupervisorFactory(specialty="medicine")
        self.pg = PGFactory(supervisor=self.supervisor, specialty="medicine", year="1")

        # Create test case using factory (handles all required fields)
        self.case = ClinicalCaseFactory(
            pg=self.pg,
            supervisor=self.supervisor,
            case_title="Acute Myocardial Infarction",
            complexity="complex",
            status="draft",
        )
        self.category = self.case.category

    def test_case_creation(self):
        """Test clinical case creation"""
        self.assertEqual(str(self.case), "Acute Myocardial Infarction - testpg")
        self.assertEqual(self.case.status, "draft")
        self.assertEqual(self.case.pg, self.pg)
        self.assertEqual(self.case.supervisor, self.supervisor)

    def test_case_status_workflow(self):
        """Test case status progression"""
        # Initially draft
        self.assertEqual(self.case.status, "draft")
        self.assertTrue(self.case.can_be_submitted())

        # Submit for review
        self.case.status = "submitted"
        self.case.submitted_at = timezone.now()
        self.case.save()

        self.assertFalse(self.case.can_be_submitted())
        self.assertTrue(self.case.can_be_reviewed())

    def test_case_completion_check(self):
        """Test case completeness validation"""
        # Case should be complete with current data
        self.assertTrue(self.case.is_complete())

        # Remove required field
        self.case.learning_points = ""
        self.case.save()
        self.assertFalse(self.case.is_complete())

    def test_case_permissions(self):
        """Test case access permissions"""
        # PG can edit their own draft case
        self.assertTrue(self.case.can_edit(self.pg))

        # Supervisor can edit assigned cases
        self.assertTrue(self.case.can_edit(self.supervisor))

        # Other users cannot edit
        other_user = PGFactory()
        self.assertFalse(self.case.can_edit(other_user))


class CaseReviewModelTest(TestCase):
    """Test the CaseReview model"""

    def setUp(self):
        # Create test users and case
        self.supervisor = SupervisorFactory(specialty="medicine")
        self.pg = PGFactory(supervisor=self.supervisor, specialty="medicine", year="1")

        self.category = CaseCategory.objects.create(name="Pediatrics", color_code="#4CAF50")

        self.case = ClinicalCase.objects.create(
            pg=self.pg,
            case_title="Pediatric Asthma",
            category=self.category,
            date_encountered=date.today(),
            patient_age=8,
            patient_gender="F",
            learning_points="Asthma management in children",
            supervisor=self.supervisor,
            status="submitted",
        )

    def test_review_creation(self):
        """Test case review creation"""
        review = CaseReview.objects.create(
            case=self.case,
            reviewer=self.supervisor,
            clinical_accuracy_score=8,
            documentation_quality_score=9,
            learning_demonstration_score=7,
            professionalism_score=10,
            overall_rating=8,
            recommendation="approved",
            comments="Excellent case presentation and analysis.",
        )

        self.assertEqual(review.case, self.case)
        self.assertEqual(review.reviewer, self.supervisor)
        self.assertEqual(review.overall_rating, 8)
        self.assertEqual(review.recommendation, "approved")

    def test_average_score_calculation(self):
        """Test automatic average score calculation"""
        review = CaseReview.objects.create(
            case=self.case,
            reviewer=self.supervisor,
            clinical_accuracy_score=8,
            documentation_quality_score=6,
            learning_demonstration_score=7,
            professionalism_score=9,
        )

        expected_average = (8 + 6 + 7 + 9) / 4
        self.assertEqual(review.calculate_average_score(), expected_average)


class CaseStatisticsModelTest(TestCase):
    """Test the CaseStatistics model"""

    def setUp(self):
        self.supervisor = SupervisorFactory(specialty="medicine")
        self.pg = PGFactory(supervisor=self.supervisor, specialty="medicine", year="1")

        self.category = CaseCategory.objects.create(name="Internal Medicine", color_code="#2196F3")

        # Create multiple cases for statistics
        for i in range(5):
            ClinicalCase.objects.create(
                pg=self.pg,
                case_title=f"Case {i + 1}",
                category=self.category,
                date_encountered=date.today() - timedelta(days=i),
                patient_age=30 + i,
                patient_gender="M" if i % 2 == 0 else "female",
                learning_points=f"Learning points for case {i + 1}",
                supervisor=self.supervisor,
                status="approved" if i < 3 else "draft",
                completion_score=80 + i if i < 3 else None,
            )

    def test_statistics_calculation(self):
        """Test automatic statistics calculation"""
        stats = CaseStatistics.objects.create(pg=self.pg)
        stats.refresh_statistics()

        self.assertEqual(stats.total_cases, 5)
        self.assertEqual(stats.approved_cases, 3)
        self.assertEqual(stats.pending_cases, 2)
        self.assertGreater(stats.average_score, 0)
        self.assertGreater(stats.completion_rate, 0)


class CaseFormsTest(TestCase):
    """Test case-related forms"""

    def setUp(self):
        self.supervisor = SupervisorFactory(specialty="medicine")
        self.pg = PGFactory(supervisor=self.supervisor, specialty="medicine", year="2")

        self.category = CaseCategory.objects.create(name="Surgery", color_code="#FF9800")

    def test_clinical_case_form_valid(self):
        """Test valid clinical case form submission"""
        diagnosis = DiagnosisFactory()
        
        form_data = {
            "case_title": "Appendectomy",
            "category": self.category.id,
            "date_encountered": str(date.today() - timedelta(days=1)),
            "patient_age": 25,
            "patient_gender": "M",
            "chief_complaint": "Right lower quadrant pain",
            "history_of_present_illness": "No significant medical history",
            "physical_examination": "Tenderness in RLQ",
            "primary_diagnosis": diagnosis.id,
            "management_plan": "Surgical intervention",
            "clinical_reasoning": "Classic appendicitis presentation",
            "learning_points": "Surgical technique and patient care",
            "supervisor": self.supervisor.id,
        }

        # Create instance with pg first to satisfy model validation
        instance = ClinicalCase(pg=self.pg)
        form = ClinicalCaseForm(data=form_data, user=self.pg, instance=instance)
        if not form.is_valid():
            self.fail(f"Form validation failed: {form.errors}")
        self.assertTrue(form.is_valid())

    def test_clinical_case_form_invalid(self):
        """Test invalid clinical case form submission"""
        form_data = {
            "case_title": "",  # Required field missing
            "category": self.category.id,
            "date_encountered": str(date.today()),
        }

        form = ClinicalCaseForm(data=form_data, user=self.pg)
        self.assertFalse(form.is_valid())
        self.assertIn("case_title", form.errors)

    def test_case_review_form_valid(self):
        """Test valid case review form"""
        # Use factory to create a complete case
        case = ClinicalCaseFactory(
            pg=self.pg,
            supervisor=self.supervisor,
            case_title="Test Case",
            category=self.category,
            status="submitted",
        )

        form_data = {
            "clinical_accuracy_score": 8,
            "documentation_quality_score": 9,
            "learning_demonstration_score": 7,
            "professionalism_score": 10,
            "overall_rating": 8,
            "recommendation": "approved",
            "comments": "Great work!",
            "is_final": True,
        }

        form = CaseReviewForm(data=form_data, case=case)
        self.assertTrue(form.is_valid())


class CaseViewsTest(TestCase):
    """Test case-related views"""

    def setUp(self):
        self.client = Client()

        # Create test users
        self.supervisor = SupervisorFactory(specialty="medicine")
        self.pg = PGFactory(supervisor=self.supervisor, specialty="medicine", year="1")

        self.admin = AdminFactory()

        # Create test data
        self.category = CaseCategory.objects.create(name="Orthopedics", color_code="#795548")

        self.case = ClinicalCase.objects.create(
            pg=self.pg,
            case_title="Fracture Management",
            category=self.category,
            date_encountered=date.today(),
            patient_age=45,
            patient_gender="M",
            learning_points="Fracture classification and treatment",
            supervisor=self.supervisor,
        )

    def test_case_list_view_pg(self):
        """Test case list view for PG user"""
        self.client.login(username="testpg", password="testpass123")
        response = self.client.get(reverse("cases:case_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.case.case_title)
        self.assertEqual(len(response.context["cases"]), 1)

    def test_case_list_view_supervisor(self):
        """Test case list view for supervisor"""
        self.client.login(username="testsupervisor", password="testpass123")
        response = self.client.get(reverse("cases:case_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.case.case_title)

    def test_case_detail_view(self):
        """Test case detail view"""
        self.client.login(username="testpg", password="testpass123")
        response = self.client.get(reverse("cases:case_detail", kwargs={"pk": self.case.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.case.case_title)
        self.assertEqual(response.context["case"], self.case)

    def test_case_create_view_pg(self):
        """Test case creation by PG"""
        self.client.login(username="testpg", password="testpass123")
        response = self.client.get(reverse("cases:case_create"))

        self.assertEqual(response.status_code, 200)

        # Test form submission
        form_data = {
            "case_title": "New Case",
            "category": self.category.id,
            "date": date.today(),
            "patient_initials": "N.C.",
            "patient_age": 35,
            "patient_gender": "female",
            "patient_history": "No history",
            "presenting_complaints": "Test complaints",
            "learning_points": "Test learning points",
            "supervisor": self.supervisor.id,
        }

        response = self.client.post(reverse("cases:case_create"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

        # Verify case was created
        new_case = ClinicalCase.objects.get(case_title="New Case")
        self.assertEqual(new_case.pg, self.pg)
        self.assertEqual(new_case.status, "draft")

    def test_case_update_view(self):
        """Test case update view"""
        self.client.login(username="testpg", password="testpass123")
        response = self.client.get(reverse("cases:case_update", kwargs={"pk": self.case.pk}))

        self.assertEqual(response.status_code, 200)

        # Test form submission
        form_data = {
            "case_title": "Updated Case Title",
            "category": self.category.id,
            "date": self.case.date,
            "patient_initials": self.case.patient_initials,
            "patient_age": self.case.patient_age,
            "patient_gender": self.case.patient_gender,
            "patient_history": "Updated history",
            "presenting_complaints": "Updated complaints",
            "learning_points": "Updated learning points",
            "supervisor": self.supervisor.id,
        }

        response = self.client.post(
            reverse("cases:case_update", kwargs={"pk": self.case.pk}), data=form_data
        )
        self.assertEqual(response.status_code, 302)

        # Verify case was updated
        updated_case = ClinicalCase.objects.get(pk=self.case.pk)
        self.assertEqual(updated_case.case_title, "Updated Case Title")

    def test_case_submit_view(self):
        """Test case submission for review"""
        self.client.login(username="testpg", password="testpass123")
        response = self.client.post(reverse("cases:case_submit", kwargs={"pk": self.case.pk}))

        self.assertEqual(response.status_code, 302)

        # Verify case status changed
        updated_case = ClinicalCase.objects.get(pk=self.case.pk)
        self.assertEqual(updated_case.status, "submitted")
        self.assertIsNotNone(updated_case.submitted_at)

    def test_unauthorized_access(self):
        """Test unauthorized access protection"""
        # Test without login
        response = self.client.get(reverse("cases:case_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test PG accessing other PG's case
        _other_pg = PGFactory()

        self.client.login(username="otherpg", password="testpass123")
        response = self.client.get(reverse("cases:case_detail", kwargs={"pk": self.case.pk}))
        self.assertEqual(response.status_code, 404)  # Case not found due to queryset filtering

    def test_statistics_view(self):
        """Test statistics dashboard"""
        self.client.login(username="testpg", password="testpass123")
        response = self.client.get(reverse("cases:case_statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("user_stats", response.context)


class CaseIntegrationTest(TestCase):
    """Integration tests for case workflow"""

    def setUp(self):
        self.client = Client()

        # Create users
        self.supervisor = SupervisorFactory(specialty="medicine")

        self.category = CaseCategory.objects.create(name="Neurology", color_code="#9C27B0")

    def test_complete_case_workflow(self):
        """Test complete case workflow from creation to review"""

        # 1. PG logs in and creates a case
        self.client.login(username="testpg", password="testpass123")

        case_data = {
            "case_title": "Stroke Management",
            "category": self.category.id,
            "date": date.today(),
            "patient_initials": "S.M.",
            "patient_age": 70,
            "patient_gender": "male",
            "patient_history": "Hypertension, smoking",
            "presenting_complaints": "Sudden weakness, speech difficulty",
            "learning_points": "Acute stroke protocols and thrombolysis",
            "supervisor": self.supervisor.id,
        }

        response = self.client.post(reverse("cases:case_create"), data=case_data)
        self.assertEqual(response.status_code, 302)

        case = ClinicalCase.objects.get(case_title="Stroke Management")
        self.assertEqual(case.status, "draft")

        # 2. PG submits the case for review
        response = self.client.post(reverse("cases:case_submit", kwargs={"pk": case.pk}))
        self.assertEqual(response.status_code, 302)

        case.refresh_from_db()
        self.assertEqual(case.status, "submitted")

        # 3. Supervisor logs in and reviews the case
        self.client.login(username="testsupervisor", password="testpass123")

        review_data = {
            "clinical_accuracy_score": 9,
            "documentation_quality_score": 8,
            "learning_demonstration_score": 9,
            "professionalism_score": 10,
            "overall_rating": 9,
            "recommendation": "approved",
            "comments": "Excellent case documentation and learning reflection.",
            "is_final": True,
        }

        response = self.client.post(
            reverse("cases:case_review", kwargs={"case_pk": case.pk}), data=review_data
        )
        self.assertEqual(response.status_code, 302)

        # 4. Verify case status and review
        case.refresh_from_db()
        self.assertEqual(case.status, "approved")

        review = CaseReview.objects.get(case=case)
        self.assertEqual(review.recommendation, "approved")
        self.assertEqual(review.overall_rating, 9)

        # 5. Verify statistics are updated
        stats, created = CaseStatistics.objects.get_or_create(pg=self.pg)
        stats.refresh_statistics()

        self.assertEqual(stats.total_cases, 1)
        self.assertEqual(stats.approved_cases, 1)
        self.assertGreater(stats.average_score, 0)
