"""
URL configuration for sims_project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

SIMS - Postgraduate Medical Training System
Created: 2025-05-29 16:10:53 UTC
Author: SMIB2012
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template.response import TemplateResponse

def home_view(request):
    """
    Home page view - redirects authenticated users to dashboard,
    shows landing page for anonymous users
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    context = {
        'system_name': settings.SIMS_SETTINGS.get('SYSTEM_NAME', 'SIMS'),
        'institution_name': settings.SIMS_SETTINGS.get('INSTITUTION_NAME', 'Medical College'),
        'contact_email': settings.SIMS_SETTINGS.get('CONTACT_EMAIL', ''),
        'contact_phone': settings.SIMS_SETTINGS.get('CONTACT_PHONE', ''),
    }
    
    return TemplateResponse(request, 'home.html', context)

def health_check(request):
    """Simple health check endpoint for monitoring"""
    return HttpResponse("OK", content_type="text/plain")

def robots_txt(request):
    """Robots.txt for SEO"""
    content = """User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /media/private/
Allow: /
"""
    return HttpResponse(content, content_type="text/plain")

urlpatterns = [
    # Home and utility URLs
    path('', home_view, name='home'),
    path('health/', health_check, name='health_check'),
    path('robots.txt', robots_txt, name='robots_txt'),    # Django Admin
    path('admin/', admin.site.urls),
    
    # SIMS App URLs (temporarily commented out to test)
    # path('users/', include('sims.users.urls')),
    # path('rotations/', include('sims.rotations.urls')),
    # path('certificates/', include('sims.certificates.urls')),
    # path('logbook/', include('sims.logbook.urls')),
    # path('cases/', include('sims.cases.urls')),
    # API URLs will be added later when needed
    # path('api/v1/', include([
    #     path('users/', include('sims.users.api_urls')),
    #     path('rotations/', include('sims.rotations.api_urls')),
    #     path('certificates/', include('sims.certificates.api_urls')),
    #     path('logbook/', include('sims.logbook.api_urls')),
    #     path('cases/', include('sims.cases.api_urls')),
    # ])),
    
    # Third-party app URLs (commented out until REST framework is configured)
    # path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar if available (commented out for now)
    # if 'debug_toolbar' in settings.INSTALLED_APPS:
    #     import debug_toolbar
    #     urlpatterns = [
    #         path('__debug__/', include(debug_toolbar.urls)),
    #     ] + urlpatterns

# Custom error handlers (commented out until views are created)
# handler404 = 'sims_project.views.handler404'
# handler500 = 'sims_project.views.handler500'
# handler403 = 'sims_project.views.handler403'
# handler400 = 'sims_project.views.handler400'

# Admin customization
admin.site.site_header = settings.SIMS_SETTINGS.get('SYSTEM_NAME', 'SIMS Administration')
admin.site.site_title = 'SIMS Admin'
admin.site.index_title = f"Welcome to {settings.SIMS_SETTINGS.get('INSTITUTION_NAME', 'Medical College')} SIMS"
admin.site.site_url = '/'  # Link to main site
admin.site.enable_nav_sidebar = True

# Additional URL patterns for specific features
urlpatterns += [
    # Quick access URLs for common actions
    path('dashboard/', lambda request: redirect('users:dashboard'), name='dashboard'),
    path('profile/', lambda request: redirect('users:profile'), name='profile'),
    path('login/', lambda request: redirect('users:login'), name='login'),
    path('logout/', lambda request: redirect('users:logout'), name='logout'),
      # Quick upload shortcuts
    path('upload/certificate/', lambda request: redirect('certificates:upload'), name='quick_upload_certificate'),
    path('upload/case/', lambda request: redirect('cases:upload'), name='quick_upload_case'),
    
    # Quick view shortcuts for supervisors
    path('pending-reviews/', lambda request: redirect('users:supervisor_dashboard'), name='pending_reviews'),
    path('my-pgs/', lambda request: redirect('users:supervisor_pgs'), name='my_pgs'),
    
    # Reports shortcuts
    path('reports/', lambda request: redirect('analytics:reports'), name='reports'),
    path('export/', lambda request: redirect('analytics:export'), name='export'),
]

# URL patterns for different deployment scenarios
if hasattr(settings, 'URL_PREFIX') and settings.URL_PREFIX:
    # If deployed under a subdirectory
    urlpatterns = [
        path(f'{settings.URL_PREFIX}/', include(urlpatterns)),
    ]

# Security headers middleware integration
if not settings.DEBUG:
    # Add security-related URL patterns for production
    urlpatterns += [
        # Security.txt for security researchers
        path('.well-known/security.txt', lambda request: HttpResponse(
            f"""Contact: {settings.SIMS_SETTINGS.get('CONTACT_EMAIL', 'security@example.com')}
Expires: 2025-12-31T23:59:59.000Z
Encryption: mailto:{settings.SIMS_SETTINGS.get('CONTACT_EMAIL', 'security@example.com')}
Preferred-Languages: en
Canonical: https://{request.get_host()}/.well-known/security.txt
Policy: https://{request.get_host()}/security-policy/
""", content_type="text/plain")),
    ]

# WebApp manifest for PWA support (future enhancement)
if settings.SIMS_SETTINGS.get('ENABLE_PWA', False):
    urlpatterns += [
        path('manifest.json', 'sims_project.views.manifest_json', name='manifest'),
        path('sw.js', 'sims_project.views.service_worker', name='service_worker'),
    ]

# Internationalization URLs (if i18n is enabled)
if settings.USE_I18N and len(settings.LANGUAGES) > 1:
    from django.conf.urls.i18n import i18n_patterns
    urlpatterns = i18n_patterns(*urlpatterns, prefix_default_language=False)

# Development-specific URLs
if settings.DEBUG:
    # Add development tools
    urlpatterns += [
        # Email preview in development
        path('dev/email-preview/', 'sims_project.dev_views.email_preview', name='dev_email_preview'),
        
        # Database schema viewer
        path('dev/schema/', 'sims_project.dev_views.schema_view', name='dev_schema'),
        
        # Test data generation
        path('dev/generate-test-data/', 'sims_project.dev_views.generate_test_data', name='dev_test_data'),
    ]

# API documentation URLs (if enabled)
if settings.SIMS_SETTINGS.get('ENABLE_API_DOCS', False):
    urlpatterns += [
        path('api/docs/', include('rest_framework.urls')),
        # Add Swagger/OpenAPI documentation if available
    ]