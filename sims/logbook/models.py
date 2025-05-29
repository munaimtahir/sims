from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
import json

User = get_user_model()

class Procedure(models.Model):
    """
    Model representing medical procedures that can be performed and logged.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    CATEGORY_CHOICES = [
        ('basic', 'Basic Procedures'),
        ('intermediate', 'Intermediate Procedures'),
        ('advanced', 'Advanced Procedures'),
        ('diagnostic', 'Diagnostic Procedures'),
        ('therapeutic', 'Therapeutic Procedures'),
        ('surgical', 'Surgical Procedures'),
        ('emergency', 'Emergency Procedures'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the procedure"
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='basic',
        help_text="Category of the procedure"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the procedure"
    )
    
    difficulty_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
        help_text="Difficulty level from 1 (basic) to 5 (expert)"
    )
    
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Typical duration in minutes"
    )
    
    cme_points = models.PositiveIntegerField(
        default=0,
        help_text="CME points typically awarded for this procedure"
    )
    
    learning_objectives = models.TextField(
        blank=True,
        help_text="Learning objectives for this procedure"
    )
    
    prerequisites = models.TextField(
        blank=True,
        help_text="Prerequisites or requirements before performing"
    )
    
    required_skills = models.ManyToManyField(
        'Skill',
        blank=True,
        related_name='required_for_procedures',
        help_text="Skills required to perform this procedure"
    )
    
    assessment_criteria = models.TextField(
        blank=True,
        help_text="Criteria for assessing competency in this procedure"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this procedure is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Procedure"
        verbose_name_plural = "Procedures"
        ordering = ['category', 'difficulty_level', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_usage_count(self):
        """Get count of logbook entries using this procedure"""
        return self.logbook_entries.count()
    
    def get_average_score(self):
        """Get average assessment score for this procedure"""
        entries = self.logbook_entries.filter(
            supervisor_assessment_score__isnull=False
        )
        if entries.exists():
            return entries.aggregate(
                avg_score=models.Avg('supervisor_assessment_score')
            )['avg_score']
        return None
    
    def get_difficulty_display_color(self):
        """Get color code for difficulty level display"""
        colors = {
            1: '#28a745',  # Green - Easy
            2: '#6c757d',  # Gray - Basic
            3: '#ffc107',  # Yellow - Intermediate
            4: '#fd7e14',  # Orange - Advanced
            5: '#dc3545',  # Red - Expert
        }
        return colors.get(self.difficulty_level, '#6c757d')

class Diagnosis(models.Model):
    """
    Model representing medical diagnoses that can be assigned to cases.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    CATEGORY_CHOICES = [
        ('cardiovascular', 'Cardiovascular'),
        ('respiratory', 'Respiratory'),
        ('gastrointestinal', 'Gastrointestinal'),
        ('neurological', 'Neurological'),
        ('endocrine', 'Endocrine'),
        ('infectious', 'Infectious Disease'),
        ('hematology', 'Hematology'),
        ('oncology', 'Oncology'),
        ('psychiatry', 'Psychiatry'),
        ('dermatology', 'Dermatology'),
        ('musculoskeletal', 'Musculoskeletal'),
        ('genitourinary', 'Genitourinary'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the diagnosis"
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text="Medical category of the diagnosis"
    )
    
    icd_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="ICD-10 or ICD-11 code"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the diagnosis"
    )
    
    typical_presentation = models.TextField(
        blank=True,
        help_text="Typical clinical presentation"
    )
    
    common_procedures = models.ManyToManyField(
        Procedure,
        blank=True,
        related_name='common_diagnoses',
        help_text="Procedures commonly associated with this diagnosis"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this diagnosis is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Diagnosis"
        verbose_name_plural = "Diagnoses"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['icd_code']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_diagnosis_per_category'
            ),
        ]
    
    def __str__(self):
        icd_display = f" ({self.icd_code})" if self.icd_code else ""
        return f"{self.name}{icd_display}"
    
    def get_usage_count(self):
        """Get total count of logbook entries with this diagnosis"""
        return (self.primary_entries.count() + 
                self.secondary_entries.count())
    
    def get_primary_usage_count(self):
        """Get count as primary diagnosis"""
        return self.primary_entries.count()
    
    def get_secondary_usage_count(self):
        """Get count as secondary diagnosis"""
        return self.secondary_entries.count()

class Skill(models.Model):
    """
    Model representing clinical skills that can be demonstrated and assessed.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    CATEGORY_CHOICES = [
        ('clinical', 'Clinical Skills'),
        ('technical', 'Technical Skills'),
        ('communication', 'Communication Skills'),
        ('professional', 'Professional Skills'),
        ('academic', 'Academic Skills'),
        ('leadership', 'Leadership Skills'),
        ('research', 'Research Skills'),
    ]
    
    LEVEL_CHOICES = [
        ('basic', 'Basic Level'),
        ('intermediate', 'Intermediate Level'),
        ('advanced', 'Advanced Level'),
        ('expert', 'Expert Level'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the skill"
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='clinical',
        help_text="Category of the skill"
    )
    
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='basic',
        help_text="Expected competency level"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the skill"
    )
    
    competency_requirements = models.TextField(
        blank=True,
        help_text="Requirements to demonstrate competency"
    )
    
    assessment_methods = models.TextField(
        blank=True,
        help_text="Methods for assessing this skill"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this skill is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ['category', 'level', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_skill_per_category'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    def get_usage_count(self):
        """Get count of logbook entries demonstrating this skill"""
        return self.logbook_entries.count()
    
    def get_level_order(self):
        """Get numeric order for level"""
        level_order = {
            'basic': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4,
        }
        return level_order.get(self.level, 1)

class LogbookTemplate(models.Model):
    """
    Model representing templates for different types of logbook entries.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    TEMPLATE_TYPE_CHOICES = [
        ('medical', 'Medical Case'),
        ('surgical', 'Surgical Case'),
        ('emergency', 'Emergency Case'),
        ('outpatient', 'Outpatient Case'),
        ('procedure', 'Procedure Focused'),
        ('research', 'Research Activity'),
        ('teaching', 'Teaching Activity'),
        ('quality', 'Quality Improvement'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the template"
    )
    
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        default='medical',
        help_text="Type of logbook entry this template is for"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of when to use this template"
    )
    
    template_structure = models.JSONField(
        default=dict,
        help_text="JSON structure defining the template layout"
    )
    
    required_fields = models.JSONField(
        default=list,
        help_text="List of required fields for this template"
    )
    
    completion_guidelines = models.TextField(
        blank=True,
        help_text="Guidelines for completing entries using this template"
    )
    
    example_entries = models.TextField(
        blank=True,
        help_text="Example entries using this template"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is a default template"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is currently active"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates',
        help_text="User who created this template"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Logbook Template"
        verbose_name_plural = "Logbook Templates"
        ordering = ['template_type', 'name']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['is_default']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def get_usage_count(self):
        """Get count of entries using this template"""
        return self.logbook_entries.count()
    
    def get_required_fields_list(self):
        """Get required fields as a formatted list"""
        if isinstance(self.required_fields, list):
            return self.required_fields
        return []
    
    def get_template_sections(self):
        """Get template sections from structure"""
        if isinstance(self.template_structure, dict):
            return self.template_structure.get('sections', [])
        return []

class LogbookEntry(models.Model):
    """
    Model representing individual logbook entries documenting clinical experiences.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('needs_revision', 'Needs Revision'),
        ('archived', 'Archived'),
    ]
    
    PATIENT_GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown/Not Specified'),
    ]
    
    # Core entry information
    pg = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logbook_entries',
        limit_choices_to={'role': 'pg'},
        help_text="Postgraduate who created this entry"
    )
    
    date = models.DateField(
        help_text="Date of the clinical encounter"
    )
    
    rotation = models.ForeignKey(
        'rotations.Rotation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logbook_entries',
        help_text="Rotation during which this case occurred"
    )
    
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_entries',
        limit_choices_to={'role__in': ['supervisor', 'admin']},
        help_text="Supervising consultant"
    )
    
    case_title = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief title or summary of the case"
    )
    
    template = models.ForeignKey(
        LogbookTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logbook_entries',
        help_text="Template used for this entry"
    )
    
    # Patient information (anonymized)
    patient_age = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        help_text="Patient age in years"
    )
    
    patient_gender = models.CharField(
        max_length=1,
        choices=PATIENT_GENDER_CHOICES,
        help_text="Patient gender"
    )
    
    patient_chief_complaint = models.TextField(
        help_text="Patient's chief complaint or presenting symptoms"
    )
    
    patient_history_summary = models.TextField(
        blank=True,
        help_text="Brief summary of relevant patient history"
    )
    
    # Clinical information
    primary_diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.SET_NULL,
        null=True,
        related_name='primary_entries',
        help_text="Primary diagnosis"
    )
    
    secondary_diagnoses = models.ManyToManyField(
        Diagnosis,
        blank=True,
        related_name='secondary_entries',
        help_text="Secondary or differential diagnoses"
    )
    
    procedures = models.ManyToManyField(
        Procedure,
        blank=True,
        related_name='logbook_entries',
        help_text="Procedures performed or observed"
    )
    
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='logbook_entries',
        help_text="Skills demonstrated during this case"
    )
    
    investigations_ordered = models.TextField(
        blank=True,
        help_text="Investigations ordered and results"
    )
    
    # Learning and reflection
    clinical_reasoning = models.TextField(
        help_text="Clinical reasoning and thought process"
    )
    
    learning_points = models.TextField(
        help_text="Key learning points from this case"
    )
    
    challenges_faced = models.TextField(
        blank=True,
        help_text="Challenges encountered and how they were addressed"
    )
    
    follow_up_required = models.TextField(
        blank=True,
        help_text="Follow-up actions or learning required"
    )
    
    # Assessment and feedback
    supervisor_feedback = models.TextField(
        blank=True,
        help_text="Supervisor's feedback on this case"
    )
    
    self_assessment_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="Self-assessment score (1-10)"
    )
    
    supervisor_assessment_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="Supervisor's assessment score (1-10)"
    )
    
    # Status and workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the entry"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_entries',
        help_text="User who created this entry"
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_entries',
        help_text="User who verified/approved this entry"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when entry was verified"
    )
    
    class Meta:
        verbose_name = "Logbook Entry"
        verbose_name_plural = "Logbook Entries"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['pg', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
            models.Index(fields=['rotation']),
            models.Index(fields=['supervisor']),
            models.Index(fields=['primary_diagnosis']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date__lte=timezone.now().date()),
                name='logbook_entry_date_not_future'
            ),
            models.CheckConstraint(
                check=models.Q(patient_age__gte=0) & models.Q(patient_age__lte=150),
                name='logbook_entry_valid_age'
            ),
        ]
    
    def __str__(self):
        title = self.case_title or f"Entry for {self.date}"
        pg_name = self.pg.get_full_name() if self.pg else "No PG"
        return f"{title} - {pg_name}"
    
    def clean(self):
        """Validate entry data"""
        errors = {}
        
        # Validate date is not in the future
        if self.date and self.date > timezone.now().date():
            errors['date'] = "Entry date cannot be in the future"
        
        # Validate date is not too old (more than 1 year)
        if self.date and self.date < (timezone.now().date() - timedelta(days=365)):
            errors['date'] = "Entry date cannot be more than 1 year old"
        
        # Validate supervisor assignment for PG's rotation
        if self.supervisor and self.pg and self.rotation:
            if (self.pg.supervisor and 
                self.supervisor != self.pg.supervisor and 
                not self.supervisor.role == 'admin'):
                errors['supervisor'] = "Supervisor should be the PG's assigned supervisor"
        
        # Validate assessment scores
        if (self.self_assessment_score and self.supervisor_assessment_score and
            abs(self.self_assessment_score - self.supervisor_assessment_score) > 5):
            errors['supervisor_assessment_score'] = (
                "Assessment scores differ significantly. Please review."
            )
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to handle status transitions and notifications"""
        # Set case title if not provided
        if not self.case_title and self.primary_diagnosis:
            self.case_title = f"{self.primary_diagnosis.name} - {self.date}"
        
        # Auto-assign supervisor from PG if not set
        if not self.supervisor and self.pg and self.pg.supervisor:
            self.supervisor = self.pg.supervisor
        
        # Handle status transitions
        if self.pk:  # Existing entry
            old_entry = LogbookEntry.objects.get(pk=self.pk)
            if old_entry.status != self.status:
                self._handle_status_change(old_entry.status, self.status)
        
        super().save(*args, **kwargs)
    
    def _handle_status_change(self, old_status, new_status):
        """Handle status change logic"""
        if new_status == 'approved':
            self.verified_at = timezone.now()
        elif new_status == 'submitted' and old_status == 'draft':
            # Send notification to supervisor
            self._notify_supervisor_of_submission()
    
    def _notify_supervisor_of_submission(self):
        """Send notification to supervisor about new submission"""
        try:
            from sims.notifications.models import Notification
            
            if self.supervisor:
                Notification.objects.create(
                    user=self.supervisor,
                    title="New Logbook Entry for Review",
                    message=f"{self.pg.get_full_name()} has submitted a logbook entry: {self.case_title}",
                    type='logbook',
                    related_object_id=self.id
                )
        except ImportError:
            pass  # Notifications app not available
    
    def get_duration_since_creation(self):
        """Get time since entry was created"""
        return timezone.now() - self.created_at
    
    def get_review_duration(self):
        """Get time taken for review if completed"""
        if self.verified_at:
            return self.verified_at - self.created_at
        return None
    
    def is_overdue(self, days=7):
        """Check if entry is overdue for completion"""
        if self.status == 'draft':
            return (timezone.now().date() - self.date).days > days
        return False
    
    def can_be_edited(self):
        """Check if entry can be edited by the PG"""
        return self.status in ['draft', 'needs_revision']
    
    def can_be_deleted(self):
        """Check if entry can be deleted"""
        return self.status in ['draft']
    
    def get_status_color(self):
        """Get color code for status display"""
        status_colors = {
            'draft': '#6c757d',        # Gray
            'submitted': '#ffc107',    # Yellow
            'approved': '#28a745',     # Green
            'needs_revision': '#fd7e14', # Orange
            'archived': '#6c757d',     # Gray
        }
        return status_colors.get(self.status, '#6c757d')
    
    def get_procedures_display(self):
        """Get formatted list of procedures"""
        procedures = self.procedures.all()
        if procedures.count() == 0:
            return "No procedures recorded"
        elif procedures.count() <= 3:
            return ", ".join([p.name for p in procedures])
        else:
            first_three = ", ".join([p.name for p in procedures[:3]])
            return f"{first_three} (+{procedures.count()-3} more)"
    
    def get_skills_display(self):
        """Get formatted list of skills"""
        skills = self.skills.all()
        if skills.count() == 0:
            return "No skills recorded"
        elif skills.count() <= 3:
            return ", ".join([s.name for s in skills])
        else:
            first_three = ", ".join([s.name for s in skills[:3]])
            return f"{first_three} (+{skills.count()-3} more)"
    
    def get_complexity_score(self):
        """Calculate complexity score based on procedures and diagnoses"""
        procedure_complexity = sum(p.difficulty_level for p in self.procedures.all())
        diagnosis_complexity = 1 if self.primary_diagnosis else 0
        diagnosis_complexity += self.secondary_diagnoses.count()
        
        return procedure_complexity + diagnosis_complexity
    
    def get_cme_points(self):
        """Calculate total CME points for this entry"""
        return sum(p.cme_points for p in self.procedures.all())
    
    def get_absolute_url(self):
        """Get URL for entry detail page"""
        return reverse('logbook:detail', kwargs={'pk': self.pk})
    
    def get_edit_url(self):
        """Get URL for entry edit page"""
        return reverse('logbook:edit', kwargs={'pk': self.pk})

class LogbookReview(models.Model):
    """
    Model for detailed reviews and feedback on logbook entries.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('needs_revision', 'Needs Revision'),
        ('rejected', 'Rejected'),
    ]
    
    logbook_entry = models.ForeignKey(
        LogbookEntry,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Logbook entry being reviewed"
    )
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logbook_reviews_given',
        limit_choices_to={'role__in': ['supervisor', 'admin']},
        help_text="Person conducting the review"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Review status"
    )
    
    review_date = models.DateField(
        default=timezone.now,
        help_text="Date when the review was conducted"
    )
    
    # Detailed feedback
    feedback = models.TextField(
        help_text="Overall feedback on the entry"
    )
    
    strengths_identified = models.TextField(
        blank=True,
        help_text="Strengths demonstrated in this case"
    )
    
    areas_for_improvement = models.TextField(
        blank=True,
        help_text="Areas requiring improvement"
    )
    
    recommendations = models.TextField(
        blank=True,
        help_text="Specific recommendations for future learning"
    )
    
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up discussion is required"
    )
    
    # Assessment scores
    clinical_knowledge_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="Clinical knowledge score (1-10)"
    )
    
    clinical_skills_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="Clinical skills score (1-10)"
    )
    
    professionalism_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="Professionalism score (1-10)"
    )
    
    overall_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="Overall performance score (1-10)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Logbook Review"
        verbose_name_plural = "Logbook Reviews"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['logbook_entry', 'status']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['review_date']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['logbook_entry', 'reviewer'],
                name='unique_review_per_reviewer_entry'
            ),
        ]
    
    def __str__(self):
        return f"Review of {self.logbook_entry.case_title or 'Entry'} by {self.reviewer.get_full_name()}"
    
    def clean(self):
        """Validate review data"""
        # Ensure reviewer has permission to review this entry
        if (self.reviewer and self.logbook_entry and
            self.reviewer.role == 'supervisor'):
            if self.logbook_entry.pg.supervisor != self.reviewer:
                raise ValidationError(
                    "Supervisor can only review entries of their assigned PGs"
                )
        
        # Validate that all component scores are provided if overall score is given
        if self.overall_score:
            if not all([self.clinical_knowledge_score, 
                       self.clinical_skills_score, 
                       self.professionalism_score]):
                raise ValidationError(
                    "All component scores must be provided when giving an overall score"
                )
    
    def save(self, *args, **kwargs):
        """Override save to update entry status"""
        super().save(*args, **kwargs)
        
        # Update logbook entry status based on review
        if self.status == 'approved':
            self.logbook_entry.status = 'approved'
            self.logbook_entry.verified_by = self.reviewer
            self.logbook_entry.verified_at = timezone.now()
            self.logbook_entry.save()
        elif self.status in ['needs_revision', 'rejected']:
            self.logbook_entry.status = 'needs_revision'
            self.logbook_entry.save()
    
    def get_average_score(self):
        """Calculate average of all component scores"""
        scores = [
            self.clinical_knowledge_score,
            self.clinical_skills_score,
            self.professionalism_score
        ]
        valid_scores = [s for s in scores if s is not None]
        
        if valid_scores:
            return sum(valid_scores) / len(valid_scores)
        return None
    
    def get_status_color(self):
        """Get color code for status display"""
        status_colors = {
            'pending': '#ffc107',        # Yellow
            'approved': '#28a745',       # Green
            'needs_revision': '#fd7e14', # Orange
            'rejected': '#dc3545',       # Red
        }
        return status_colors.get(self.status, '#6c757d')
    
    def is_complete(self):
        """Check if review is complete with all required fields"""
        return (self.feedback and 
                self.status != 'pending' and
                self.overall_score is not None)

class LogbookStatistics(models.Model):
    """
    Model for storing and tracking logbook statistics for individual PGs.
    
    Created: 2025-05-29 17:19:21 UTC
    Author: SMIB2012
    """
    
    pg = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='logbook_stats',
        limit_choices_to={'role': 'pg'},
        help_text="Postgraduate these statistics belong to"
    )
    
    # Entry statistics
    total_entries = models.PositiveIntegerField(default=0)
    draft_entries = models.PositiveIntegerField(default=0)
    submitted_entries = models.PositiveIntegerField(default=0)
    approved_entries = models.PositiveIntegerField(default=0)
    revision_entries = models.PositiveIntegerField(default=0)
    
    # Procedure statistics
    total_procedures = models.PositiveIntegerField(default=0)
    unique_procedures = models.PositiveIntegerField(default=0)
    
    # Skill statistics
    total_skills = models.PositiveIntegerField(default=0)
    unique_skills = models.PositiveIntegerField(default=0)
    
    # Assessment statistics
    average_self_score = models.FloatField(null=True, blank=True)
    average_supervisor_score = models.FloatField(null=True, blank=True)
    average_review_score = models.FloatField(null=True, blank=True)
    
    # Learning metrics
    total_cme_points = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)  # Percentage
    
    # Timing statistics
    average_review_time = models.FloatField(null=True, blank=True)  # Days
    last_entry_date = models.DateField(null=True, blank=True)
    most_active_month = models.CharField(max_length=7, blank=True)  # YYYY-MM format
    
    # Quality metrics
    entries_needing_revision_rate = models.FloatField(default=0.0)  # Percentage
    on_time_submission_rate = models.FloatField(default=0.0)  # Percentage
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Logbook Statistics"
        verbose_name_plural = "Logbook Statistics"
    
    def __str__(self):
        return f"Logbook Stats for {self.pg.get_full_name()}"
    
    def update_statistics(self):
        """Update all statistics based on current logbook entries"""
        entries = self.pg.logbook_entries.all()
        
        # Basic entry counts
        self.total_entries = entries.count()
        self.draft_entries = entries.filter(status='draft').count()
        self.submitted_entries = entries.filter(status='submitted').count()
        self.approved_entries = entries.filter(status='approved').count()
        self.revision_entries = entries.filter(status='needs_revision').count()
        
        # Procedure statistics
        procedure_entries = entries.filter(procedures__isnull=False).distinct()
        self.total_procedures = sum(e.procedures.count() for e in procedure_entries)
        self.unique_procedures = entries.values('procedures').distinct().count()
        
        # Skill statistics
        skill_entries = entries.filter(skills__isnull=False).distinct()
        self.total_skills = sum(e.skills.count() for e in skill_entries)
        self.unique_skills = entries.values('skills').distinct().count()
        
        # Assessment scores
        scored_entries = entries.filter(self_assessment_score__isnull=False)
        if scored_entries.exists():
            self.average_self_score = scored_entries.aggregate(
                avg=models.Avg('self_assessment_score')
            )['avg']
        
        supervisor_scored = entries.filter(supervisor_assessment_score__isnull=False)
        if supervisor_scored.exists():
            self.average_supervisor_score = supervisor_scored.aggregate(
                avg=models.Avg('supervisor_assessment_score')
            )['avg']
        
        # Review scores
        reviews = LogbookReview.objects.filter(
            logbook_entry__pg=self.pg,
            overall_score__isnull=False
        )
        if reviews.exists():
            self.average_review_score = reviews.aggregate(
                avg=models.Avg('overall_score')
            )['avg']
        
        # CME points
        approved_entries = entries.filter(status='approved')
        self.total_cme_points = sum(e.get_cme_points() for e in approved_entries)
        
        # Completion rate (approved vs total)
        if self.total_entries > 0:
            self.completion_rate = (self.approved_entries / self.total_entries) * 100
        
        # Timing statistics
        self.last_entry_date = entries.order_by('-date').first().date if entries.exists() else None
        
        # Review time
        reviewed_entries = entries.filter(verified_at__isnull=False)
        if reviewed_entries.exists():
            review_times = []
            for entry in reviewed_entries:
                review_duration = entry.get_review_duration()
                if review_duration:
                    review_times.append(review_duration.days)
            
            if review_times:
                self.average_review_time = sum(review_times) / len(review_times)
        
        # Quality metrics
        if self.total_entries > 0:
            self.entries_needing_revision_rate = (self.revision_entries / self.total_entries) * 100
        
        # On-time submission rate (within 7 days of encounter)
        on_time_count = 0
        for entry in entries:
            days_to_submit = (entry.created_at.date() - entry.date).days
            if days_to_submit <= 7:
                on_time_count += 1
        
        if self.total_entries > 0:
            self.on_time_submission_rate = (on_time_count / self.total_entries) * 100
        
        # Most active month
        if entries.exists():
            monthly_counts = entries.extra({
                'month': "to_char(date, 'YYYY-MM')"
            }).values('month').annotate(
                count=models.Count('id')
            ).order_by('-count')
            
            if monthly_counts:
                self.most_active_month = monthly_counts[0]['month']
        
        self.save()
    
    @classmethod
    def update_all_statistics(cls):
        """Update statistics for all PGs"""
        for pg in User.objects.filter(role='pg', is_active=True):
            stats, created = cls.objects.get_or_create(pg=pg)
            stats.update_statistics()
    
    def get_performance_trend(self):
        """Get performance trend over time"""
        # This could calculate month-over-month improvements
        # For now, return a simple indicator
        if self.average_supervisor_score and self.average_self_score:
            if self.average_supervisor_score > self.average_self_score:
                return "improving"
            elif self.average_supervisor_score < self.average_self_score:
                return "needs_attention"
            else:
                return "stable"
        return "insufficient_data"
    
    def get_completion_status(self):
        """Get completion status indicator"""
        if self.completion_rate >= 90:
            return "excellent"
        elif self.completion_rate >= 70:
            return "good"
        elif self.completion_rate >= 50:
            return "fair"
        else:
            return "poor"