from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta

from .models import CaseCategory, ClinicalCase, CaseReview, CaseStatistics

User = get_user_model()

class CaseCategoryForm(forms.ModelForm):
    """Form for creating and editing case categories"""
    
    class Meta:
        model = CaseCategory
        fields = ['name', 'description', 'color_code', 'sort_order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color_code': forms.TextInput(attrs={'type': 'color'}),
            'sort_order': forms.NumberInput(attrs={'min': 0}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check for duplicate names (excluding current instance if editing)
            qs = CaseCategory.objects.filter(name__iexact=name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('A category with this name already exists.')
        return name

class ClinicalCaseForm(forms.ModelForm):
    """Form for creating and editing clinical cases"""
    
    class Meta:
        model = ClinicalCase
        fields = [
            'date', 'rotation', 'supervisor', 'case_title', 'category',
            'patient_age', 'patient_gender', 'patient_chief_complaint',
            'patient_history_summary', 'patient_examination_findings',
            'primary_diagnosis', 'differential_diagnoses', 'procedures_performed',
            'investigation_results', 'treatment_plan', 'learning_objectives',
            'learning_points', 'reflection', 'skills_demonstrated',
            'challenges_faced', 'case_presentation', 'follow_up_notes',
            'case_files', 'case_images', 'submission_notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'patient_chief_complaint': forms.Textarea(attrs={'rows': 2}),
            'patient_history_summary': forms.Textarea(attrs={'rows': 3}),
            'patient_examination_findings': forms.Textarea(attrs={'rows': 3}),
            'differential_diagnoses': forms.Textarea(attrs={'rows': 2}),
            'procedures_performed': forms.Textarea(attrs={'rows': 2}),
            'investigation_results': forms.Textarea(attrs={'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'rows': 3}),
            'learning_objectives': forms.Textarea(attrs={'rows': 2}),
            'learning_points': forms.Textarea(attrs={'rows': 3}),
            'reflection': forms.Textarea(attrs={'rows': 4}),
            'skills_demonstrated': forms.Textarea(attrs={'rows': 2}),
            'challenges_faced': forms.Textarea(attrs={'rows': 3}),
            'case_presentation': forms.Textarea(attrs={'rows': 4}),
            'follow_up_notes': forms.Textarea(attrs={'rows': 3}),
            'submission_notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self._setup_user_specific_fields(user)
        
        # Make certain fields required based on status
        if self.instance.pk and self.instance.status == 'submitted':
            self._make_submission_fields_required()
    
    def _setup_user_specific_fields(self, user):
        """Setup form fields based on user role"""
        if user.role == 'pg':
            # PGs can only assign cases to themselves
            self.fields['pg'].widget = forms.HiddenInput()
            self.fields['pg'].initial = user
            
            # Filter rotations to only current user's rotations
            from sims.rotations.models import Rotation
            self.fields['rotation'].queryset = Rotation.objects.filter(
                pg=user, is_active=True
            )
            
            # Remove supervisor field (will be set automatically)
            if 'supervisor' in self.fields:
                self.fields['supervisor'].widget = forms.HiddenInput()
                self.fields['supervisor'].initial = user.supervisor
        
        elif user.role == 'supervisor':
            # Supervisors can assign cases to their PGs
            self.fields['pg'].queryset = User.objects.filter(
                role='pg', supervisor=user, is_active=True
            )
            self.fields['supervisor'].widget = forms.HiddenInput()
            self.fields['supervisor'].initial = user
        
        # Filter categories to active only
        self.fields['category'].queryset = CaseCategory.objects.filter(is_active=True)
        
        # Filter diagnoses to active only
        from sims.logbook.models import Diagnosis
        self.fields['primary_diagnosis'].queryset = Diagnosis.objects.filter(is_active=True)
    
    def _make_submission_fields_required(self):
        """Make certain fields required for submission"""
        required_fields = [
            'case_title', 'patient_chief_complaint', 'primary_diagnosis',
            'learning_objectives', 'learning_points'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_date(self):
        case_date = self.cleaned_data.get('date')
        if case_date:
            # Case date cannot be in the future
            if case_date > date.today():
                raise ValidationError('Case date cannot be in the future.')
            
            # Case date cannot be more than 6 months old
            six_months_ago = date.today() - timedelta(days=180)
            if case_date < six_months_ago:
                raise ValidationError('Case date cannot be more than 6 months old.')
        
        return case_date
    
    def clean_patient_age(self):
        age = self.cleaned_data.get('patient_age')
        if age is not None:
            if age < 0 or age > 150:
                raise ValidationError('Please enter a valid patient age (0-150).')
        return age
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate required fields for submission
        if cleaned_data.get('status') == 'submitted':
            required_fields = ['case_title', 'patient_chief_complaint', 'primary_diagnosis']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for submission.')
        
        return cleaned_data

class CaseReviewForm(forms.ModelForm):
    """Form for creating and editing case reviews"""
    
    class Meta:
        model = CaseReview
        fields = [
            'case', 'clinical_assessment_score', 'differential_diagnosis_score',
            'investigation_score', 'management_score', 'learning_score',
            'feedback', 'strengths', 'areas_for_improvement', 'recommendations',
            'status'
        ]
        widgets = {
            'clinical_assessment_score': forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 0.5}),
            'differential_diagnosis_score': forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 0.5}),
            'investigation_score': forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 0.5}),
            'management_score': forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 0.5}),
            'learning_score': forms.NumberInput(attrs={'min': 1, 'max': 10, 'step': 0.5}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 3}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self._setup_user_specific_fields(user)
    
    def _setup_user_specific_fields(self, user):
        """Setup form fields based on user role"""
        if user.role == 'supervisor':
            # Supervisors can only review cases of their PGs
            self.fields['case'].queryset = ClinicalCase.objects.filter(
                pg__supervisor=user, status='submitted'
            )
        elif user.role == 'pg':
            # PGs can view but not edit reviews (read-only)
            for field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True
                self.fields[field].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that all scores are provided if status is complete
        if cleaned_data.get('status') == 'completed':
            score_fields = [
                'clinical_assessment_score', 'differential_diagnosis_score',
                'investigation_score', 'management_score', 'learning_score'
            ]
            
            for field in score_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'All scores must be provided for completed reviews.')
        
        return cleaned_data

class CaseStatisticsForm(forms.ModelForm):
    """Form for creating and editing case statistics"""
    
    class Meta:
        model = CaseStatistics
        fields = ['pg', 'period_start', 'period_end']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role == 'supervisor':
            # Supervisors can only create statistics for their PGs
            self.fields['pg'].queryset = User.objects.filter(
                role='pg', supervisor=user, is_active=True
            )
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end:
            if period_start >= period_end:
                raise ValidationError('Period start date must be before end date.')
            
            # Check for overlapping periods for the same PG
            pg = cleaned_data.get('pg')
            if pg:
                overlapping = CaseStatistics.objects.filter(
                    pg=pg,
                    period_start__lt=period_end,
                    period_end__gt=period_start
                )
                
                if self.instance.pk:
                    overlapping = overlapping.exclude(pk=self.instance.pk)
                
                if overlapping.exists():
                    raise ValidationError('This period overlaps with existing statistics for this PG.')
        
        return cleaned_data

# Search and Filter Forms
class CaseSearchForm(forms.Form):
    """Form for searching and filtering clinical cases"""
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search cases by title, patient complaint, or diagnosis...',
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=CaseCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + ClinicalCase.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    pg = forms.ModelChoiceField(
        queryset=User.objects.filter(role='pg', is_active=True),
        required=False,
        empty_label="All PGs",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role == 'supervisor':
            # Supervisors can only see their PGs
            self.fields['pg'].queryset = User.objects.filter(
                role='pg', supervisor=user, is_active=True
            )
        elif user and user.role == 'pg':
            # PGs don't need the PG filter
            del self.fields['pg']

class CaseReviewSearchForm(forms.Form):
    """Form for searching and filtering case reviews"""
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search reviews by case title or feedback...',
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + CaseReview.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    score_range = forms.ChoiceField(
        choices=[
            ('', 'All Scores'),
            ('9-10', 'Excellent (9-10)'),
            ('7-8', 'Good (7-8)'),
            ('5-6', 'Satisfactory (5-6)'),
            ('1-4', 'Needs Improvement (1-4)')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
