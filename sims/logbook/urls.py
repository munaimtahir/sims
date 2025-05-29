from django.urls import path
from . import views

app_name = 'logbook'

urlpatterns = [
    # Main logbook views
    path('', views.LogbookEntryListView.as_view(), name='list'),
    path('dashboard/', views.LogbookDashboardView.as_view(), name='dashboard'),
    path('analytics/', views.LogbookAnalyticsView.as_view(), name='analytics'),
    
    # Entry management
    path('entry/create/', views.LogbookEntryCreateView.as_view(), name='create'),
    path('entry/quick/', views.QuickLogbookEntryView.as_view(), name='quick_create'),
    path('entry/<int:pk>/', views.LogbookEntryDetailView.as_view(), name='detail'),
    path('entry/<int:pk>/edit/', views.LogbookEntryUpdateView.as_view(), name='edit'),
    path('entry/<int:pk>/delete/', views.LogbookEntryDeleteView.as_view(), name='delete'),
    
    # Review management
    path('entry/<int:entry_pk>/review/', 
         views.LogbookReviewCreateView.as_view(), 
         name='review'),
    path('review/<int:pk>/', 
         views.LogbookReviewDetailView.as_view(), 
         name='review_detail'),
    
    # Bulk operations
    path('bulk-actions/', 
         views.BulkLogbookActionView.as_view(), 
         name='bulk_actions'),
    
    # Export and reporting
    path('export/csv/', views.export_logbook_csv, name='export_csv'),
    
    # AJAX/API endpoints
    path('api/stats/', views.logbook_stats_api, name='stats_api'),
    path('api/template/<int:template_id>/preview/', 
         views.template_preview_api, 
         name='template_preview_api'),
    path('api/entry/<int:entry_id>/complexity/', 
         views.entry_complexity_api, 
         name='entry_complexity_api'),
    path('api/update-statistics/', 
         views.update_logbook_statistics, 
         name='update_stats_api'),
]

# Additional URL patterns for mobile app and external integrations
api_urlpatterns = [
    # REST API endpoints would go here
    # These would be included in the main API routing
]