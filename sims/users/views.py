from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import User
from .forms import UserProfileForm, PGSearchForm, SupervisorAssignmentForm
from .decorators import (
    admin_required, supervisor_required, pg_required,
    AdminRequiredMixin, SupervisorRequiredMixin, PGRequiredMixin,
    SupervisorOrAdminRequiredMixin, supervisor_or_admin_required
)
import json

# Authentication Views
def login_view(request):
    """Custom login view with role-based redirection"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active and not user.is_archived:
                login(request, user)
                
                # Role-based redirection
                if user.is_admin():
                    messages.success(request, f'Welcome back, Admin {user.get_display_name()}!')
                    return redirect('users:admin_dashboard')
                elif user.is_supervisor():
                    messages.success(request, f'Welcome back, Dr. {user.get_display_name()}!')
                    return redirect('users:supervisor_dashboard')
                elif user.is_pg():
                    messages.success(request, f'Welcome back, {user.get_display_name()}!')
                    return redirect('users:pg_dashboard')
                else:
                    return redirect('users:profile')
            else:
                messages.error(request, 'Your account is inactive. Please contact admin.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    """Custom logout view"""
    user_name = request.user.get_display_name()
    logout(request)
    messages.info(request, f'Goodbye {user_name}! You have been logged out.')
    return redirect('users:login')

# Dashboard Views
@admin_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    
    # Get statistics
    total_users = User.objects.filter(is_archived=False).count()
    total_pgs = User.objects.filter(role='pg', is_archived=False).count()
    total_supervisors = User.objects.filter(role='supervisor', is_archived=False).count()
    new_users_this_month = User.objects.filter(
        date_joined__month=timezone.now().month,
        date_joined__year=timezone.now().year
    ).count()
    
    # Recent activity
    recent_users = User.objects.filter(is_archived=False).order_by('-date_joined')[:5]
    
    # Specialty distribution
    specialty_stats = User.objects.filter(
        role__in=['pg', 'supervisor'], 
        is_archived=False
    ).values('specialty').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Convert to JSON for JavaScript consumption
    import json
    specialty_stats_json = json.dumps([
        {
            'specialty': item['specialty'] or 'Unspecified',
            'count': item['count']
        }
        for item in specialty_stats
    ])
    
    context = {
        'total_users': total_users,
        'total_pgs': total_pgs,
        'total_supervisors': total_supervisors,
        'new_users_this_month': new_users_this_month,
        'recent_users': recent_users,
        'specialty_stats': specialty_stats,
        'specialty_stats_json': specialty_stats_json,
        'dashboard_type': 'admin'
    }
    return render(request, 'users/admin_dashboard.html', context)

@supervisor_required
def supervisor_dashboard(request):
    """Supervisor dashboard with assigned PGs overview"""
    
    # Get assigned PGs
    assigned_pgs = request.user.get_assigned_pgs()
    
    # Get pending documents count
    pending_count = request.user.get_documents_pending_count()
    
    # Recent submissions from assigned PGs
    # Import here to avoid circular imports
    from django.contrib.contenttypes.models import ContentType
    recent_submissions = []
    
    # Get recent activity from all assigned PGs
    for pg in assigned_pgs:
        # You can add logic here to get recent submissions
        pass
    
    context = {
        'assigned_pgs': assigned_pgs,
        'assigned_pgs_count': assigned_pgs.count(),
        'pending_documents': pending_count,
        'recent_submissions': recent_submissions[:10],
        'dashboard_type': 'supervisor'
    }
    return render(request, 'users/supervisor_dashboard.html', context)

@pg_required
def pg_dashboard(request):
    """PG dashboard with personal progress overview"""
    
    # Get document counts
    documents_submitted = request.user.get_documents_submitted_count()
    
    # Get supervisor info
    supervisor = request.user.supervisor
    
    # Get recent submissions
    recent_submissions = []
      # Get progress statistics
    # Import here to avoid circular imports
    from sims.certificates.models import Certificate
    from sims.rotations.models import Rotation
    from sims.logbook.models import LogbookEntry
    from sims.cases.models import ClinicalCase
    
    progress_stats = {
        'certificates': Certificate.objects.filter(pg=request.user).count(),
        'rotations': Rotation.objects.filter(pg=request.user).count(),
        'logbook_entries': LogbookEntry.objects.filter(pg=request.user).count(),
        'clinical_cases': ClinicalCase.objects.filter(pg=request.user).count(),
    }
    
    context = {
        'documents_submitted': documents_submitted,
        'supervisor': supervisor,
        'recent_submissions': recent_submissions[:10],
        'progress_stats': progress_stats,
        'dashboard_type': 'pg'
    }
    return render(request, 'users/pg_dashboard.html', context)


class DashboardRedirectView(LoginRequiredMixin, View):
    """Redirect users to appropriate dashboard based on their role"""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin():
            return redirect('users:admin_dashboard')
        elif user.is_supervisor():
            return redirect('users:supervisor_dashboard')
        elif user.is_pg():
            return redirect('users:pg_dashboard')
        else:
            return redirect('users:profile')


class AdminDashboardView(AdminRequiredMixin, View):
    """Admin dashboard class-based view"""
    
    def get(self, request, *args, **kwargs):
        return admin_dashboard(request)


class SupervisorDashboardView(SupervisorRequiredMixin, View):
    """Supervisor dashboard class-based view"""
    
    def get(self, request, *args, **kwargs):
        return supervisor_dashboard(request)


class PGDashboardView(PGRequiredMixin, View):
    """PG dashboard class-based view"""
    
    def get(self, request, *args, **kwargs):
        return pg_dashboard(request)


# Profile Views
class ProfileView(LoginRequiredMixin, DetailView):
    """User's own profile view"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user


class ProfileDetailView(SupervisorOrAdminRequiredMixin, DetailView):
    """View another user's profile (admin/supervisor only)"""
    model = User
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile_user'


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user's own profile"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user


# User Management Views (Admin only)
class UserListView(AdminRequiredMixin, ListView):
    """List all users (admin only)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        return User.objects.filter(is_archived=False).order_by('last_name', 'first_name')


class UserCreateView(AdminRequiredMixin, View):
    """Create new user (admin only)"""
    
    def get(self, request):
        return render(request, 'users/user_create.html')
    
    def post(self, request):
        # Implementation for user creation
        return redirect('users:user_list')


class UserEditView(AdminRequiredMixin, UpdateView):
    """Edit user (admin only)"""
    model = User
    fields = ['first_name', 'last_name', 'email', 'role', 'specialty', 'year', 'is_active']
    template_name = 'users/user_edit.html'
    success_url = reverse_lazy('users:user_list')


class UserDeleteView(AdminRequiredMixin, View):
    """Archive user (admin only)"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_archived = True
        user.save()
        messages.success(request, f'User {user.get_display_name()} has been archived.')
        return redirect('users:user_list')


class UserActivateView(AdminRequiredMixin, View):
    """Activate/deactivate user (admin only)"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.get_display_name()} has been {status}.')
        return redirect('users:user_list')


class UserDeactivateView(UserActivateView):
    """Deactivate user (admin only) - same as UserActivateView"""
    pass


class UserArchiveView(AdminRequiredMixin, View):
    """Archive user (admin only)"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_archived = True
        user.save()
        messages.success(request, f'User {user.get_display_name()} has been archived.')
        return redirect('users:user_list')


# Supervisor Management Views
class SupervisorListView(AdminRequiredMixin, ListView):
    """List all supervisors (admin only)"""
    model = User
    template_name = 'users/supervisor_list.html'
    context_object_name = 'supervisors'
    
    def get_queryset(self):
        return User.objects.filter(role='supervisor', is_archived=False)


class SupervisorPGsView(LoginRequiredMixin, DetailView):
    """View supervisor's assigned PGs"""
    model = User
    template_name = 'users/supervisor_pgs.html'
    context_object_name = 'supervisor'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.pk == kwargs.get('pk')):
            raise PermissionDenied("Only admins or the supervisor themselves can view this")
        return super().dispatch(request, *args, **kwargs)


class AssignSupervisorView(AdminRequiredMixin, View):
    """Assign supervisor to PG (admin only)"""
    
    def get(self, request):
        form = SupervisorAssignmentForm()
        return render(request, 'users/assign_supervisor.html', {'form': form})
    
    def post(self, request):
        form = SupervisorAssignmentForm(request.POST)
        if form.is_valid():
            # Implementation for supervisor assignment
            messages.success(request, 'Supervisor assigned successfully.')
            return redirect('users:pg_list')
        return render(request, 'users/assign_supervisor.html', {'form': form})


# PG Management Views  
@supervisor_or_admin_required
def pg_list_view(request):
    """List PGs for supervisors and admins"""
    if request.user.is_supervisor():
        # Supervisors see only their assigned PGs
        pgs = request.user.get_assigned_pgs()
    elif request.user.is_admin():
        # Admins see all PGs
        pgs = User.objects.filter(role='pg', is_archived=False)
    
    # Search functionality
    form = PGSearchForm(request.GET)
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        if search_query:
            pgs = pgs.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        
        specialty = form.cleaned_data.get('specialty')
        if specialty:
            pgs = pgs.filter(specialty=specialty)
        
        year = form.cleaned_data.get('year')
        if year:
            pgs = pgs.filter(year=year)
    
    paginator = Paginator(pgs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_pgs': pgs.count(),
    }
    return render(request, 'users/pg_list.html', context)


class PGListView(LoginRequiredMixin, View):
    """List PGs - class-based wrapper"""
    
    def get(self, request):
        return pg_list_view(request)


class PGBulkUploadView(AdminRequiredMixin, View):
    """Bulk upload PGs (admin only)"""
    
    def get(self, request):
        return render(request, 'users/pg_bulk_upload.html')
    
    def post(self, request):
        # Implementation for bulk upload
        messages.success(request, 'PGs uploaded successfully.')
        return redirect('users:pg_list')


class PGProgressView(LoginRequiredMixin, DetailView):
    """View PG's progress"""
    model = User
    template_name = 'users/pg_progress.html'
    context_object_name = 'pg_user'
    
    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if not (request.user.is_admin() or 
                request.user.is_supervisor() or 
                request.user.pk == user.pk):
            raise PermissionDenied("Access denied")
        return super().dispatch(request, *args, **kwargs)


# Reports and Analytics Views
class UserReportsView(AdminRequiredMixin, View):
    """User reports (admin only)"""
    
    def get(self, request):
        return render(request, 'users/user_reports.html')


class UserExportView(AdminRequiredMixin, View):
    """Export user data (admin only)"""
    
    def get(self, request):
        # Implementation for data export
        return JsonResponse({'status': 'success'})


class ActivityLogView(AdminRequiredMixin, ListView):
    """Activity log view (admin only)"""
    template_name = 'users/activity_log.html'
    context_object_name = 'activities'
    paginate_by = 50
    
    def get_queryset(self):
        # Placeholder - would need an ActivityLog model
        return []


# API Views
class UserSearchAPIView(LoginRequiredMixin, View):
    """Search users API"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        )[:10]
        
        results = [{'id': user.id, 'name': user.get_display_name()} for user in users]
        return JsonResponse({'results': results})


class SupervisorsBySpecialtyAPIView(LoginRequiredMixin, View):
    """Get supervisors by specialty API"""
    
    def get(self, request, specialty):
        supervisors = User.objects.filter(
            role='supervisor',
            specialty=specialty,
            is_active=True,
            is_archived=False
        )
        
        results = [{'id': sup.id, 'name': sup.get_display_name()} for sup in supervisors]
        return JsonResponse({'supervisors': results})


class UserStatsAPIView(LoginRequiredMixin, View):
    """Get user statistics API"""
    
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        # Check permissions
        if not (request.user.is_admin() or 
                request.user.is_supervisor() or 
                request.user.pk == user.pk):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        stats = {
            'total_cases': 0,  # Would come from cases app
            'total_certificates': 0,  # Would come from certificates app
            'total_rotations': 0,  # Would come from rotations app
            'logbook_entries': 0,  # Would come from logbook app
        }
        
        return JsonResponse(stats)

# Analytics Views
@admin_required
def admin_analytics_view(request):
    """Admin analytics with system-wide statistics"""
    
    # System overview stats
    total_users = User.objects.filter(is_archived=False).count()
    active_users = User.objects.filter(is_active=True, is_archived=False).count()
    total_pgs = User.objects.filter(role='pg', is_archived=False).count()
    total_supervisors = User.objects.filter(role='supervisor', is_archived=False).count()
      # Monthly user registration stats
    from django.db.models import Count
    from django.utils import timezone
    from datetime import datetime, timedelta
    import json
    
    # Specialty distribution
    specialty_distribution = User.objects.filter(
        role__in=['pg', 'supervisor'],
        is_archived=False
    ).values('specialty').annotate(count=Count('id')).order_by('-count')
    
    # Convert to JSON for JavaScript consumption
    specialty_stats_json = json.dumps([
        {
            'specialty': item['specialty'] or 'Unspecified',
            'count': item['count']
        }
        for item in specialty_distribution
    ])
    
    # Progress tracking statistics
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_pgs': total_pgs,
        'total_supervisors': total_supervisors,
        'specialty_distribution': list(specialty_distribution),
        'specialty_stats_json': specialty_stats_json,
        'analytics_type': 'admin'
    }
    return render(request, 'users/admin_analytics.html', context)


@supervisor_required
def supervisor_analytics_view(request):
    """Supervisor analytics with assigned PGs statistics"""
    
    # Get assigned PGs
    assigned_pgs = request.user.get_assigned_pgs()
    assigned_pgs_count = assigned_pgs.count()
    
    # PG progress statistics
    pg_progress_stats = []
    for pg in assigned_pgs:
        try:
            from sims.certificates.models import Certificate
            from sims.logbook.models import LogbookEntry
            from sims.rotations.models import Rotation
            
            pg_stats = {
                'pg': pg,
                'certificates': Certificate.objects.filter(pg=pg).count(),
                'logbook_entries': LogbookEntry.objects.filter(pg=pg).count(),
                'rotations': Rotation.objects.filter(pg=pg).count(),
                'completion_percentage': 0  # Calculate based on requirements
            }
            pg_progress_stats.append(pg_stats)
        except ImportError:
            pg_stats = {
                'pg': pg,
                'certificates': 0,
                'logbook_entries': 0,
                'rotations': 0,
                'completion_percentage': 0
            }
            pg_progress_stats.append(pg_stats)
    
    # Monthly progress data for assigned PGs
    from django.utils import timezone
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    try:
        from sims.logbook.models import LogbookEntry
        monthly_entries = LogbookEntry.objects.filter(
            pg__in=assigned_pgs,
            created_at__month=current_month,
            created_at__year=current_year
        ).count()
    except ImportError:
        monthly_entries = 0
    
    try:
        from sims.certificates.models import Certificate
        monthly_certificates = Certificate.objects.filter(
            pg__in=assigned_pgs,
            created_at__month=current_month,
            created_at__year=current_year
        ).count()
    except ImportError:
        monthly_certificates = 0
    
    context = {
        'assigned_pgs_count': assigned_pgs_count,
        'pg_progress_stats': pg_progress_stats,
        'monthly_entries': monthly_entries,
        'monthly_certificates': monthly_certificates,
        'analytics_type': 'supervisor'
    }
    return render(request, 'users/supervisor_analytics.html', context)


@pg_required
def pg_analytics_view(request):
    """PG analytics with personal progress tracking"""
    
    # Personal progress statistics
    try:
        from sims.certificates.models import Certificate
        my_certificates = Certificate.objects.filter(pg=request.user).count()
        certificates_this_month = Certificate.objects.filter(
            pg=request.user,
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count()
    except ImportError:
        my_certificates = 0
        certificates_this_month = 0
    
    try:
        from sims.logbook.models import LogbookEntry
        my_logbook_entries = LogbookEntry.objects.filter(pg=request.user).count()
        entries_this_month = LogbookEntry.objects.filter(
            pg=request.user,
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count()
        
        # Monthly progress chart data (last 6 months)
        from datetime import datetime, timedelta
        six_months_ago = timezone.now().date() - timedelta(days=180)
        monthly_progress = LogbookEntry.objects.filter(
            pg=request.user,
            created_at__date__gte=six_months_ago
        ).extra(
            select={'month': 'strftime("%%Y-%%m", created_at)'}
        ).values('month').annotate(count=Count('id')).order_by('month')
        
    except ImportError:
        my_logbook_entries = 0
        entries_this_month = 0
        monthly_progress = []
    
    try:
        from sims.rotations.models import Rotation
        my_rotations = Rotation.objects.filter(pg=request.user).count()
        completed_rotations = Rotation.objects.filter(
            pg=request.user, 
            status='completed'
        ).count()
        current_rotation = Rotation.objects.filter(
            pg=request.user, 
            status='active'
        ).first()
    except ImportError:
        my_rotations = 0
        completed_rotations = 0
        current_rotation = None
    
    try:
        from sims.cases.models import ClinicalCase
        my_cases = ClinicalCase.objects.filter(pg=request.user).count()
    except ImportError:
        my_cases = 0
    
    # Calculate overall completion percentage
    # This would be based on program requirements
    total_required = 100  # Placeholder - should come from program requirements
    completed = my_certificates + completed_rotations
    completion_percentage = min((completed / total_required) * 100, 100) if total_required > 0 else 0
    
    context = {
        'my_certificates': my_certificates,
        'certificates_this_month': certificates_this_month,
        'my_logbook_entries': my_logbook_entries,
        'entries_this_month': entries_this_month,
        'my_rotations': my_rotations,
        'completed_rotations': completed_rotations,
        'current_rotation': current_rotation,
        'my_cases': my_cases,
        'completion_percentage': round(completion_percentage, 1),
        'monthly_progress': list(monthly_progress),
        'analytics_type': 'pg'
    }
    return render(request, 'users/pg_analytics.html', context)