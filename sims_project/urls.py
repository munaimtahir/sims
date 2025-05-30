"""
URL configuration for sims_project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

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
    
    return HttpResponse("Welcome to SIMS - Specialized Information Management System")

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
    path('robots.txt', robots_txt, name='robots_txt'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    # SIMS App URLs
    path('users/', include('sims.users.urls')),
    path('rotations/', include('sims.rotations.urls')),
    path('certificates/', include('sims.certificates.urls')),
    path('logbook/', include('sims.logbook.urls')),
    path('cases/', include('sims.cases.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin customization
admin.site.site_header = 'SIMS Administration'
admin.site.site_title = 'SIMS Admin'
admin.site.index_title = 'Welcome to SIMS'
admin.site.site_url = '/'
admin.site.enable_nav_sidebar = True
