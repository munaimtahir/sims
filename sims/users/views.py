from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import User
from .forms import UserProfileForm, PGSearchForm, SupervisorAssignmentForm
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
@login_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    if not request.user.is_admin():
        raise PermissionDenied("Only admins can access this dashboard")
    
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
    
    context = {
        'total_users': total_users,
        'total_pgs': total_pgs,
        'total_supervisors': total_supervisors,
        'new_users_this_month': new_users_this_month,
        'recent_users': recent_users,
        'specialty_stats': specialty_stats,
        'dashboard_type': 'admin'
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
def supervisor_dashboard(request):
    """Supervisor dashboard with assigned PGs overview"""
    if not request.user.is_supervisor():
        raise PermissionDenied("Only supervisors can access this dashboard")
    
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

@login_required
def pg_dashboard(request):
    """PG dashboard with personal progress overview"""
    if not request.user.is_pg():
        raise PermissionDenied("Only PGs can access this dashboard")
    
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
    from sims.workshops.models import WorkshopCertificate
    from sims.logbook.models import LogbookEntry
    from sims.cases.models import ClinicalCase
    
    progress_stats = {
        'certificates': Certificate.objects.filter(pg=request.user).count(),
        'rotations': Rotation.objects.filter(pg=request.user).count(),
        'workshops': WorkshopCertificate.objects.filter(pg=request.user).count(),
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

# Profile Views
@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    """User profile view"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        # Allow viewing own profile or if admin/supervisor has permission
        pk = self.kwargs.get('pk')
        if pk:
            user = get_object_or_404(User, pk=pk)
            if self.request.user.is_admin():
                return user
            elif self.request.user.is_supervisor() and user.supervisor == self.request.user:
                return user
            elif user == self.request.user:
                return user
            else:
                raise PermissionDenied("You don't have permission to view this profile")
        return self.request.user

@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    """Edit user profile"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    
    def get_object(self):
        # Allow editing own profile
        pk = self.kwargs.get('pk')
        if pk and pk != str(self.request.user.pk):
            if not self.request.user.is_admin():
                raise PermissionDenied("You can only edit your own profile")
            return get_object_or_404(User, pk=pk)
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, 'Profile updated successfully!')
        return reverse_lazy('users:profile', kwargs={'pk': self.object.pk})

# User Management Views (Admin only)
@method_decorator(login_required, name='dispatch')
class UserListView(ListView):
    """List all users (admin only)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 25
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can access user management")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.filter(is_archived=False)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filter by role
        role_filter = self.request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        # Filter by specialty
        specialty_filter = self.request.GET.get('specialty')
        if specialty_filter:
            queryset = queryset.filter(specialty=specialty_filter)
        
        return queryset.order_by('role', 'last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['specialty_filter'] = self.request.GET.get('specialty', '')
        context['user_roles'] = User._meta.get_field('role').choices
        context['specialties'] = User._meta.get_field('specialty').choices
        return context

@login_required
def pg_list_view(request):
    """List PGs for supervisors"""
    if request.user.is_supervisor():
        # Supervisors see only their assigned PGs
        pgs = request.user.get_assigned_pgs()
    elif request.user.is_admin():
        # Admins see all PGs
        pgs = User.objects.filter(role='pg', is_archived=False)
    else:
        raise PermissionDenied("Only supervisors and admins can view PG lists")
    
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
    page