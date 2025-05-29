from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
import json

from .models import (
    LogbookEntry, LogbookReview, LogbookTemplate, Procedure, 
    Diagnosis, Skill, LogbookStatistics
)
from .forms import (
    LogbookEntryCreateForm, LogbookReviewForm, BulkLogbookActionForm,
    LogbookSearchForm, QuickLogbookEntryForm
)

User = get_user_model()

class ProcedureModelTests(TestCase):
    """
    Test cases for the Procedure model.
    
    Created: 2025-05-29 17:34:26 UTC
    Author: SMIB2012
    """
    
    def test_procedure_creation(self):
        """Test basic procedure creation"""
        procedure = Procedure.objects.create(
            name="Venipuncture",
            category="basic",
            description="Basic blood sampling procedure",
            difficulty_level=1,
            duration_minutes=15,
            cme_points=2
        )
        
        self.assertEqual(procedure.name, "Venipuncture")
        self.assertEqual(procedure.category, "basic")
        self.assertEqual(procedure.difficulty_level, 1)
        self.assertTrue(procedure.is_active)
    
    def test_procedure_string_representation(self):
        """Test the __str__ method"""
        procedure = Procedure.objects.create(
            name="Central Line Insertion",
            category="advanced",
            difficulty_level=4
        )
        expected = "Central Line Insertion (Advanced Procedures)"
        self.assertEqual(str(procedure), expected)
    
    def test_procedure_difficulty_color(self):
        """Test difficulty level color assignment"""
        procedure = Procedure.objects.create(
            name="Test Procedure",
            category="basic",
            difficulty_level=1
        )
        
        color = procedure.get_difficulty_display_color()
        self.assertEqual(color, '#28a745')  # Green for level 1
        
        procedure.difficulty_level = 5
        color = procedure.get_difficulty_display_color()
        self.assertEqual(color, '#dc3545')  # Red for level 5

class DiagnosisModelTests(TestCase):
    """Test cases for the Diagnosis model"""
    
    def test_diagnosis_creation(self):
        """Test basic diagnosis creation"""
        diagnosis = Diagnosis.objects.create(
            name="Hypertension",
            category="cardiovascular",
            icd_code="I10",
            description="Primary hypertension"
        )
        
        self.assertEqual(diagnosis.name, "Hypertension")
        self.assertEqual(diagnosis.category, "cardiovascular")
        self.assertEqual(diagnosis.icd_code, "I10")
        self.assertTrue(diagnosis.is_active)
    
    def test_diagnosis_string_representation(self):
        """Test the __str__ method"""
        diagnosis = Diagnosis.objects.create(
            name="Myocardial Infarction",
            category="cardiovascular",
            icd_code="I21"
        )
        expected = "Myocardial Infarction (I21)"
        self.assertEqual(str(diagnosis), expected)
    
    def test_diagnosis_unique_constraint(self):
        """Test unique constraint on name and category"""
        Diagnosis.objects.create(
            name="Pneumonia",
            category="respiratory"
        )
        
        # Should raise error for duplicate name in same category
        with self.assertRaises(Exception):
            Diagnosis.objects.create(
                name="Pneumonia",
                category="respiratory"
            )

class SkillModelTests(TestCase):
    """Test cases for the Skill model"""
    
    def test_skill_creation(self):
        """Test basic skill creation"""
        skill = Skill.objects.create(
            name="History Taking",
            category="clinical",
            level="basic",
            description="Comprehensive patient history"
        )
        
        self.assertEqual(skill.name, "History Taking")
        self.assertEqual(skill.category, "clinical")
        self.assertEqual(skill.level, "basic")
        self.assertTrue(skill.is_active)
    
    def test_skill_level_order(self):
        """Test skill level ordering"""
        skill = Skill.objects.create(
            name="Advanced Procedures",
            category="technical",
            level="advanced"
        )
        
        order = skill.get_level_order()
        self.assertEqual(order, 3)  # Advanced = 3

class LogbookTemplateModelTests(TestCase):
    """Test cases for the LogbookTemplate model"""
    
    def test_template_creation(self):
        """Test basic template creation"""
        template = LogbookTemplate.objects.create(
            name="General Medical Case",
            template_type="medical",
            description="Standard template for medical cases",
            template_structure={
                "sections": ["Patient Presentation", "Assessment", "Plan"]
            },
            required_fields=["patient_age", "primary_diagnosis"],
            is_default=True
        )
        
        self.assertEqual(template.name, "General Medical Case")
        self.assertEqual(template.template_type, "medical")
        self.assertTrue(template.is_default)
        self.assertTrue(template.is_active)
    
    def test_template_methods(self):
        """Test template utility methods"""
        template = LogbookTemplate.objects.create(
            name="Test Template",
            template_type="surgical",
            template_structure={
                "sections": ["Pre-op", "Procedure", "Post-op"]
            },
            required_fields=["procedures", "skills"]
        )
        
        sections = template.get_template_sections()
        self.assertEqual(sections, ["Pre-op", "Procedure", "Post-op"])
        
        required_fields = template.get_required_fields_list()
        self.assertEqual(required_fields, ["procedures", "skills"])

class LogbookEntryModelTests(TestCase):
    """Test cases for the LogbookEntry model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin",
            first_name="Admin",
            last_name="User"
        )
        
        self.supervisor = User.objects.create_user(
            username="supervisor_test",
            email="supervisor@test.com",
            password="testpass123",
            role="supervisor",
            first_name="Super",
            last_name="Visor"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg",
            first_name="Post",
            last_name="Graduate",
            supervisor=self.supervisor
        )
        
        # Create test clinical data
        self.diagnosis = Diagnosis.objects.create(
            name="Pneumonia",
            category="respiratory",
            icd_code="J18"
        )
        
        self.procedure = Procedure.objects.create(
            name="Chest X-ray",
            category="diagnostic",
            difficulty_level=1
        )
        
        self.skill = Skill.objects.create(
            name="Physical Examination",
            category="clinical",
            level="basic"
        )
        
        # Create rotation
        from sims.rotations.models import Department, Hospital, Rotation
        
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            address="123 Test St",
            phone="555-0123",
            email="info@test.com"
        )
        
        self.department = Department.objects.create(
            name="Internal Medicine",
            hospital=self.hospital,
            head_of_department=self.supervisor
        )
        
        self.rotation = Rotation.objects.create(
            pg=self.pg_user,
            department=self.department,
            hospital=self.hospital,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            supervisor=self.supervisor
        )
    
    def test_logbook_entry_creation(self):
        """Test basic logbook entry creation"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            rotation=self.rotation,
            supervisor=self.supervisor,
            case_title="Pneumonia Case",
            patient_age=45,
            patient_gender="M",
            patient_chief_complaint="Cough and fever",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Patient presented with typical pneumonia symptoms",
            learning_points="Learned about pneumonia diagnosis and treatment",
            created_by=self.admin_user
        )
        
        self.assertEqual(entry.pg, self.pg_user)
        self.assertEqual(entry.primary_diagnosis, self.diagnosis)
        self.assertEqual(entry.status, "draft")
        self.assertFalse(entry.is_overdue())
    
    def test_entry_string_representation(self):
        """Test the __str__ method"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            case_title="Test Case",
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test reasoning",
            learning_points="Test learning"
        )
        
        expected = f"Test Case - {self.pg_user.get_full_name()}"
        self.assertEqual(str(entry), expected)
    
    def test_entry_validation(self):
        """Test entry validation rules"""
        # Test future date validation
        entry = LogbookEntry(
            pg=self.pg_user,
            date=date.today() + timedelta(days=1),  # Future date
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test"
        )
        
        with self.assertRaises(ValidationError):
            entry.full_clean()
    
    def test_entry_auto_title_generation(self):
        """Test automatic title generation"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=45,
            patient_gender="M",
            patient_chief_complaint="Cough",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test"
        )
        
        # Title should be auto-generated
        self.assertIn("Pneumonia", entry.case_title)
        self.assertIn("45y", entry.case_title)
    
    def test_entry_permissions(self):
        """Test entry permission methods"""
        # Draft entry can be edited and deleted
        draft_entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="draft"
        )
        
        self.assertTrue(draft_entry.can_be_edited())
        self.assertTrue(draft_entry.can_be_deleted())
        
        # Approved entry cannot be edited or deleted
        approved_entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="approved"
        )
        
        self.assertFalse(approved_entry.can_be_edited())
        self.assertFalse(approved_entry.can_be_deleted())
    
    def test_entry_complexity_calculation(self):
        """Test complexity score calculation"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test"
        )
        
        # Add procedures and secondary diagnoses
        entry.procedures.add(self.procedure)
        
        secondary_diagnosis = Diagnosis.objects.create(
            name="COPD",
            category="respiratory"
        )
        entry.secondary_diagnoses.add(secondary_diagnosis)
        
        complexity = entry.get_complexity_score()
        # Should be: 1 (primary diagnosis) + 1 (secondary diagnosis) + 1 (procedure difficulty)
        self.assertEqual(complexity, 3)
    
    def test_entry_cme_points(self):
        """Test CME points calculation"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test"
        )
        
        # Procedure with CME points
        procedure_with_cme = Procedure.objects.create(
            name="Advanced Procedure",
            category="advanced",
            difficulty_level=4,
            cme_points=10
        )
        
        entry.procedures.add(procedure_with_cme)
        
        cme_points = entry.get_cme_points()
        self.assertEqual(cme_points, 10)
    
    def test_overdue_detection(self):
        """Test overdue entry detection"""
        # Create old draft entry
        old_entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today() - timedelta(days=10),  # 10 days old
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="draft"
        )
        
        self.assertTrue(old_entry.is_overdue())
        
        # Recent entry should not be overdue
        recent_entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today() - timedelta(days=2),
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="draft"
        )
        
        self.assertFalse(recent_entry.is_overdue())

class LogbookReviewModelTests(TestCase):
    """Test cases for the LogbookReview model"""
    
    def setUp(self):
        """Set up test data"""
        self.supervisor = User.objects.create_user(
            username="supervisor_test",
            email="supervisor@test.com",
            password="testpass123",
            role="supervisor"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg",
            supervisor=self.supervisor
        )
        
        self.diagnosis = Diagnosis.objects.create(
            name="Test Diagnosis",
            category="other"
        )
        
        self.entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test reasoning",
            learning_points="Test learning",
            status="submitted"
        )
    
    def test_review_creation(self):
        """Test basic review creation"""
        review = LogbookReview.objects.create(
            logbook_entry=self.entry,
            reviewer=self.supervisor,
            status="approved",
            feedback="Good work on this case",
            clinical_knowledge_score=8,
            clinical_skills_score=7,
            professionalism_score=9,
            overall_score=8
        )
        
        self.assertEqual(review.logbook_entry, self.entry)
        self.assertEqual(review.reviewer, self.supervisor)
        self.assertEqual(review.status, "approved")
    
    def test_review_updates_entry_status(self):
        """Test that review status updates entry status"""
        review = LogbookReview.objects.create(
            logbook_entry=self.entry,
            reviewer=self.supervisor,
            status="approved",
            feedback="Approved",
            clinical_knowledge_score=8,
            clinical_skills_score=8,
            professionalism_score=8,
            overall_score=8
        )
        
        # Entry should be updated to approved
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.status, "approved")
        self.assertEqual(self.entry.verified_by, self.supervisor)
        self.assertIsNotNone(self.entry.verified_at)
    
    def test_review_validation(self):
        """Test review validation rules"""
        # Test that PG cannot review entries
        invalid_review = LogbookReview(
            logbook_entry=self.entry,
            reviewer=self.pg_user,  # PG trying to review
            status="approved",
            feedback="Test"
        )
        
        with self.assertRaises(ValidationError):
            invalid_review.full_clean()
    
    def test_average_score_calculation(self):
        """Test average score calculation"""
        review = LogbookReview.objects.create(
            logbook_entry=self.entry,
            reviewer=self.supervisor,
            status="approved",
            feedback="Good work",
            clinical_knowledge_score=8,
            clinical_skills_score=6,
            professionalism_score=9,
            overall_score=8
        )
        
        avg_score = review.get_average_score()
        expected_avg = (8 + 6 + 9) / 3
        self.assertEqual(avg_score, expected_avg)
    
    def test_review_completeness(self):
        """Test review completeness check"""
        complete_review = LogbookReview.objects.create(
            logbook_entry=self.entry,
            reviewer=self.supervisor,
            status="approved",
            feedback="Complete feedback",
            overall_score=8
        )
        
        self.assertTrue(complete_review.is_complete())
        
        incomplete_review = LogbookReview.objects.create(
            logbook_entry=self.entry,
            reviewer=self.supervisor,
            status="pending",
            feedback="",
        )
        
        self.assertFalse(incomplete_review.is_complete())

class LogbookStatisticsModelTests(TestCase):
    """Test cases for the LogbookStatistics model"""
    
    def setUp(self):
        """Set up test data"""
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg"
        )
        
        self.diagnosis = Diagnosis.objects.create(
            name="Test Diagnosis",
            category="other"
        )
        
        self.procedure = Procedure.objects.create(
            name="Test Procedure",
            category="basic",
            cme_points=5
        )
    
    def test_statistics_creation_and_update(self):
        """Test statistics creation and update"""
        # Create statistics object
        stats = LogbookStatistics.objects.create(pg=self.pg_user)
        
        # Initially should be zero
        self.assertEqual(stats.total_entries, 0)
        self.assertEqual(stats.approved_entries, 0)
        
        # Create entries
        approved_entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="approved",
            supervisor_assessment_score=8
        )
        approved_entry.procedures.add(self.procedure)
        
        draft_entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=25,
            patient_gender="F",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="draft"
        )
        
        # Update statistics
        stats.update_statistics()
        
        self.assertEqual(stats.total_entries, 2)
        self.assertEqual(stats.approved_entries, 1)
        self.assertEqual(stats.draft_entries, 1)
        self.assertEqual(stats.total_cme_points, 5)
        self.assertEqual(stats.completion_rate, 50.0)
        self.assertEqual(stats.average_supervisor_score, 8.0)
    
    def test_performance_trend(self):
        """Test performance trend calculation"""
        stats = LogbookStatistics.objects.create(
            pg=self.pg_user,
            average_self_score=7.0,
            average_supervisor_score=8.0
        )
        
        trend = stats.get_performance_trend()
        self.assertEqual(trend, "improving")
        
        stats.average_supervisor_score = 6.0
        trend = stats.get_performance_trend()
        self.assertEqual(trend, "needs_attention")
    
    def test_completion_status(self):
        """Test completion status indicator"""
        stats = LogbookStatistics.objects.create(
            pg=self.pg_user,
            completion_rate=95.0
        )
        
        status = stats.get_completion_status()
        self.assertEqual(status, "excellent")
        
        stats.completion_rate = 75.0
        status = stats.get_completion_status()
        self.assertEqual(status, "good")
        
        stats.completion_rate = 30.0
        status = stats.get_completion_status()
        self.assertEqual(status, "poor")

class LogbookViewTests(TestCase):
    """Test cases for logbook views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin"
        )
        
        self.supervisor = User.objects.create_user(
            username="supervisor_test",
            email="supervisor@test.com",
            password="testpass123",
            role="supervisor"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg",
            supervisor=self.supervisor
        )
        
        # Create test data
        self.diagnosis = Diagnosis.objects.create(
            name="Test Diagnosis",
            category="other"
        )
        
        self.entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test reasoning",
            learning_points="Test learning",
            status="draft",
            created_by=self.admin_user
        )
    
    def test_entry_list_view_access(self):
        """Test access to entry list view"""
        # Unauthenticated access should redirect
        response = self.client.get(reverse('logbook:list'))
        self.assertEqual(response.status_code, 302)
        
        # Authenticated access should work
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('logbook:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logbook')
    
    def test_entry_detail_view(self):
        """Test entry detail view"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(
            reverse('logbook:detail', kwargs={'pk': self.entry.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.entry.case_title)
    
    def test_entry_create_view_permissions(self):
        """Test entry creation permissions"""
        # PGs should be able to create entries
        self.client.login(username='pg_test', password='testpass123')
        response = self.client.get(reverse('logbook:create'))
        self.assertEqual(response.status_code, 200)
        
        # Admins should also be able to create entries
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('logbook:create'))
        self.assertEqual(response.status_code, 200)
    
    def test_entry_dashboard_view(self):
        """Test dashboard view"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('logbook:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_review_permissions(self):
        """Test review permissions"""
        # Submit entry first
        self.entry.status = 'submitted'
        self.entry.save()
        
        # PGs should not be able to review entries
        self.client.login(username='pg_test', password='testpass123')
        response = self.client.get(
            reverse('logbook:review', kwargs={'entry_pk': self.entry.pk})
        )
        self.assertEqual(response.status_code, 403)
        
        # Supervisors should be able to review their PGs' entries
        self.client.login(username='supervisor_test', password='testpass123')
        response = self.client.get(
            reverse('logbook:review', kwargs={'entry_pk': self.entry.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_role_based_entry_filtering(self):
        """Test that users only see entries they have permission to view"""
        # Create another PG with different supervisor
        other_supervisor = User.objects.create_user(
            username="other_supervisor",
            email="other@test.com",
            password="testpass123",
            role="supervisor"
        )
        
        other_pg = User.objects.create_user(
            username="other_pg",
            email="otherpg@test.com",
            password="testpass123",
            role="pg",
            supervisor=other_supervisor
        )
        
        other_entry = LogbookEntry.objects.create(
            pg=other_pg,
            date=date.today(),
            patient_age=25,
            patient_gender="F",
            patient_chief_complaint="Other complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Other reasoning",
            learning_points="Other learning"
        )
        
        # Supervisor should only see their PG's entries
        self.client.login(username='supervisor_test', password='testpass123')
        response = self.client.get(reverse('logbook:list'))
        content = response.content.decode()
        self.assertIn(self.entry.case_title, content)
        self.assertNotIn(other_entry.case_title or "Other", content)
        
        # PG should only see their own entries
        self.client.login(username='pg_test', password='testpass123')
        response = self.client.get(reverse('logbook:list'))
        content = response.content.decode()
        self.assertIn(self.entry.case_title, content)
        self.assertNotIn(other_entry.case_title or "Other", content)

class LogbookFormTests(TestCase):
    """Test cases for logbook forms"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin"
        )
        
        self.supervisor = User.objects.create_user(
            username="supervisor_test",
            email="supervisor@test.com",
            password="testpass123",
            role="supervisor"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg",
            supervisor=self.supervisor
        )
        
        self.diagnosis = Diagnosis.objects.create(
            name="Test Diagnosis",
            category="other"
        )
        
        self.procedure = Procedure.objects.create(
            name="Test Procedure",
            category="basic"
        )
        
        self.skill = Skill.objects.create(
            name="Test Skill",
            category="clinical"
        )
    
    def test_entry_create_form_valid_data(self):
        """Test entry creation form with valid data"""
        form_data = {
            'pg': self.pg_user.id,
            'date': date.today(),
            'case_title': 'Test Case',
            'patient_age': 30,
            'patient_gender': 'M',
            'patient_chief_complaint': 'Test complaint',
            'primary_diagnosis': self.diagnosis.id,
            'clinical_reasoning': 'Test reasoning',
            'learning_points': 'Test learning points',
            'self_assessment_score': 7
        }
        
        form = LogbookEntryCreateForm(data=form_data, user=self.admin_user)
        self.assertTrue(form.is_valid())
    
    def test_entry_create_form_invalid_dates(self):
        """Test entry creation form with invalid dates"""
        form_data = {
            'pg': self.pg_user.id,
            'date': date.today() + timedelta(days=1),  # Future date
            'patient_age': 30,
            'patient_gender': 'M',
            'patient_chief_complaint': 'Test',
            'primary_diagnosis': self.diagnosis.id,
            'clinical_reasoning': 'Test',
            'learning_points': 'Test',
        }
        
        form = LogbookEntryCreateForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
    
    def test_review_form_valid_data(self):
        """Test review form with valid data"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="submitted"
        )
        
        form_data = {
            'status': 'approved',
            'review_date': date.today(),
            'feedback': 'Good work on this case, comprehensive approach',
            'clinical_knowledge_score': 8,
            'clinical_skills_score': 7,
            'professionalism_score': 9,
            'overall_score': 8
        }
        
        form = LogbookReviewForm(
            data=form_data,
            entry=entry,
            user=self.supervisor
        )
        self.assertTrue(form.is_valid())
    
    def test_review_form_insufficient_feedback(self):
        """Test that review form requires detailed feedback"""
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="submitted"
        )
        
        form_data = {
            'status': 'approved',
            'review_date': date.today(),
            'feedback': 'Good',  # Too short
            'clinical_knowledge_score': 8,
            'clinical_skills_score': 7,
            'professionalism_score': 9,
            'overall_score': 8
        }
        
        form = LogbookReviewForm(
            data=form_data,
            entry=entry,
            user=self.supervisor
        )
        self.assertFalse(form.is_valid())
        self.assertIn('feedback', form.errors)
    
    def test_bulk_action_form(self):
        """Test bulk action form"""
        entry1 = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test 1",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="submitted"
        )
        
        entry2 = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=25,
            patient_gender="F",
            patient_chief_complaint="Test 2",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test",
            learning_points="Test",
            status="submitted"
        )
        
        form_data = {
            'entries': [entry1.id, entry2.id],
            'action': 'approve',
            'bulk_comments': 'Bulk approval test'
        }
        
        form = BulkLogbookActionForm(data=form_data, user=self.admin_user)
        self.assertTrue(form.is_valid())
    
    def test_quick_entry_form(self):
        """Test quick entry form"""
        form_data = {
            'date': date.today(),
            'case_title': 'Quick Entry Test',
            'patient_age': 40,
            'patient_gender': 'F',
            'patient_chief_complaint': 'Quick complaint',
            'primary_diagnosis': self.diagnosis.id,
            'learning_points': 'Quick learning points'
        }
        
        form = QuickLogbookEntryForm(data=form_data, user=self.pg_user)
        self.assertTrue(form.is_valid())
    
    def test_auto_title_generation(self):
        """Test automatic title generation in forms"""
        form_data = {
            'pg': self.pg_user.id,
            'date': date.today(),
            'patient_age': 45,
            'patient_gender': 'M',
            'patient_chief_complaint': 'Chest pain',
            'primary_diagnosis': self.diagnosis.id,
            'clinical_reasoning': 'Detailed reasoning',
            'learning_points': 'Key learning points'
            # No case_title provided
        }
        
        form = LogbookEntryCreateForm(data=form_data, user=self.admin_user)
        self.assertTrue(form.is_valid())
        
        # Check that title was auto-generated
        cleaned_data = form.cleaned_data
        self.assertIn('45y', cleaned_data['case_title'])
        self.assertIn('Male', cleaned_data['case_title'])
        self.assertIn(self.diagnosis.name, cleaned_data['case_title'])

class LogbookAPITests(TestCase):
    """Test cases for logbook API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg"
        )
        
        self.diagnosis = Diagnosis.objects.create(
            name="API Test Diagnosis",
            category="other"
        )
        
        self.entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            patient_age=30,
            patient_gender="M",
            patient_chief_complaint="Test complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Test reasoning",
            learning_points="Test learning",
            status="draft"
        )
    
    def test_stats_api(self):
        """Test statistics API"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('logbook:stats_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('by_status', data)
        self.assertEqual(data['total'], 1)
    
    def test_entry_complexity_api(self):
        """Test entry complexity API"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(
            reverse('logbook:entry_complexity_api', kwargs={'entry_id': self.entry.id})
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('complexity_score', data)
        self.assertIn('cme_points', data)
        self.assertIn('procedure_count', data)
    
    def test_update_statistics_api(self):
        """Test statistics update API"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('logbook:update_stats_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_unauthorized_api_access(self):
        """Test that unauthorized users cannot access APIs"""
        # Test without login
        response = self.client.get(reverse('logbook:stats_api'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with PG user trying to update statistics
        self.client.login(username='pg_test', password='testpass123')
        response = self.client.get(reverse('logbook:update_stats_api'))
        self.assertEqual(response.status_code, 403)

class LogbookExportTests(TestCase):
    """Test cases for logbook export functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg"
        )
        
        self.diagnosis = Diagnosis.objects.create(
            name="Export Test Diagnosis",
            category="other"
        )
        
        # Create test entry
        self.entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            case_title="Export Test Entry",
            patient_age=35,
            patient_gender="F",
            patient_chief_complaint="Export test complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Export test reasoning",
            learning_points="Export test learning",
            status="approved",
            created_by=self.admin_user
        )
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('logbook:export_csv'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Check if entry data is in the CSV
        content = response.content.decode('utf-8')
        self.assertIn(self.entry.case_title, content)
        self.assertIn(self.pg_user.get_full_name(), content)
        self.assertIn(str(self.entry.patient_age), content)

class LogbookIntegrationTests(TestCase):
    """Integration tests for logbook workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin"
        )
        
        self.supervisor = User.objects.create_user(
            username="supervisor_test",
            email="supervisor@test.com",
            password="testpass123",
            role="supervisor"
        )
        
        self.pg_user = User.objects.create_user(
            username="pg_test",
            email="pg@test.com",
            password="testpass123",
            role="pg",
            supervisor=self.supervisor
        )
        
        self.diagnosis = Diagnosis.objects.create(
            name="Integration Test Diagnosis",
            category="other"
        )
        
        self.procedure = Procedure.objects.create(
            name="Integration Test Procedure",
            category="basic",
            cme_points=5
        )
        
        self.skill = Skill.objects.create(
            name="Integration Test Skill",
            category="clinical"
        )
    
    def test_complete_logbook_workflow(self):
        """Test the complete logbook workflow from creation to approval"""
        # 1. PG creates entry
        self.client.login(username='pg_test', password='testpass123')
        
        entry_data = {
            'date': date.today(),
            'case_title': 'Integration Test Case',
            'patient_age': 42,
            'patient_gender': 'M',
            'patient_chief_complaint': 'Integration test complaint',
            'primary_diagnosis': self.diagnosis.id,
            'procedures': [self.procedure.id],
            'skills': [self.skill.id],
            'clinical_reasoning': 'Comprehensive clinical reasoning for integration test',
            'learning_points': 'Key learning points from this integration test case',
            'self_assessment_score': 7
        }
        
        response = self.client.post(reverse('logbook:create'), data=entry_data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Check that entry was created
        entry = LogbookEntry.objects.get(pg=self.pg_user)
        self.assertEqual(entry.case_title, 'Integration Test Case')
        self.assertEqual(entry.status, 'draft')
        
        # 2. PG submits entry for review
        entry.status = 'submitted'
        entry.save()
        
        # 3. View entry details
        response = self.client.get(
            reverse('logbook:detail', kwargs={'pk': entry.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Login as supervisor and review entry
        self.client.login(username='supervisor_test', password='testpass123')
        
        review_data = {
            'status': 'approved',
            'review_date': date.today(),
            'feedback': 'Excellent case presentation with thorough clinical reasoning and good learning points',
            'strengths_identified': 'Strong clinical reasoning and comprehensive patient assessment',
            'recommendations': 'Continue developing diagnostic skills in similar cases',
            'clinical_knowledge_score': 8,
            'clinical_skills_score': 7,
            'professionalism_score': 9,
            'overall_score': 8
        }
        
        response = self.client.post(
            reverse('logbook:review', kwargs={'entry_pk': entry.pk}),
            data=review_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after review
        
        # Check that entry was approved
        entry.refresh_from_db()
        self.assertEqual(entry.status, 'approved')
        self.assertEqual(entry.verified_by, self.supervisor)
        self.assertIsNotNone(entry.verified_at)
        
        # Check that review was created
        review = LogbookReview.objects.get(logbook_entry=entry)
        self.assertEqual(review.status, 'approved')
        self.assertEqual(review.reviewer, self.supervisor)
        self.assertEqual(review.overall_score, 8)
        
        # 5. Verify statistics are updated
        stats, created = LogbookStatistics.objects.get_or_create(pg=self.pg_user)
        stats.update_statistics()
        
        self.assertEqual(stats.total_entries, 1)
        self.assertEqual(stats.approved_entries, 1)
        self.assertEqual(stats.total_cme_points, 5)
        self.assertEqual(stats.completion_rate, 100.0)
    
    def test_entry_revision_workflow(self):
        """Test entry revision and resubmission workflow"""
        # Create submitted entry
        entry = LogbookEntry.objects.create(
            pg=self.pg_user,
            date=date.today(),
            case_title="Revision Test Entry",
            patient_age=30,
            patient_gender="F",
            patient_chief_complaint="Test complaint",
            primary_diagnosis=self.diagnosis,
            clinical_reasoning="Initial reasoning",
            learning_points="Initial learning points",
            status="submitted"
        )
        
        # 1. Supervisor requests revision
        self.client.login(username='supervisor_test', password='testpass123')
        
        review_data = {
            'status': 'needs_revision',
            'review_date': date.today(),
            'feedback': 'Please expand on the clinical reasoning and add more specific learning points',
            'areas_for_improvement': 'Clinical reasoning needs more detail about differential diagnosis',
            'recommendations': 'Review similar cases and expand on diagnostic process',
            'clinical_knowledge_score': 6,
            'clinical_skills_score': 6,
            'professionalism_score': 8,
            'overall_score': 6
        }
        
        response = self.client.post(
            reverse('logbook:review', kwargs={'entry_pk': entry.pk}),
            data=review_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Check entry status
        entry.refresh_from_db()
        self.assertEqual(entry.status, 'needs_revision')
        
        # 2. PG edits entry (should be allowed for needs_revision status)
        self.client.login(username='pg_test', password='testpass123')
        
        response = self.client.get(
            reverse('logbook:edit', kwargs={'pk': entry.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Update entry
        updated_data = {
            'date': entry.date,
            'case_title': 'Revised Test Entry',
            'patient_age': entry.patient_age,
            'patient_gender': entry.patient_gender,
            'patient_chief_complaint': entry.patient_chief_complaint,
            'primary_diagnosis': self.diagnosis.id,
            'clinical_reasoning': 'Expanded clinical reasoning with detailed differential diagnosis analysis',
            'learning_points': 'Comprehensive learning points including diagnostic process and clinical decision making',
            'self_assessment_score': 8
        }
        
        response = self.client.post(
            reverse('logbook:edit', kwargs={'pk': entry.pk}),
            data=updated_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Check that entry was updated and status reset
        entry.refresh_from_db()
        self.assertEqual(entry.case_title, 'Revised Test Entry')
        self.assertEqual(entry.status, 'draft')  # Should reset to draft after revision
        
        # 3. Resubmit for review
        entry.status = 'submitted'
        entry.save()
        
        # 4. Supervisor approves revised entry
        self.client.login(username='supervisor_test', password='testpass123')
        
        approval_data = {
            'status': 'approved',
            'review_date': date.today(),
            'feedback': 'Much improved! Excellent clinical reasoning and comprehensive learning points',
            'strengths_identified': 'Strong improvement in clinical reasoning and reflection',
            'clinical_knowledge_score': 8,
            'clinical_skills_score': 8,
            'professionalism_score': 9,
            'overall_score': 8
        }
        
        response = self.client.post(
            reverse('logbook:review', kwargs={'entry_pk': entry.pk}),
            data=approval_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Final checks
        entry.refresh_from_db()
        self.assertEqual(entry.status, 'approved')
        
        # Should have two reviews now
        reviews = LogbookReview.objects.filter(logbook_entry=entry)
        self.assertEqual(reviews.count(), 2)
        
        latest_review = reviews.order_by('-created_at').first()
        self.assertEqual(latest_review.status, 'approved')
        self.assertEqual(latest_review.overall_score, 8)