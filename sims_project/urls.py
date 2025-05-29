from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('sims.users.urls')),
    path('rotations/', include('sims.rotations.urls')),
    path('certificates/', include('sims.certificates.urls')),
    path('workshops/', include('sims.workshops.urls')),
    path('logbook/', include('sims.logbook.urls')),
    path('cases/', include('sims.cases.urls')),
    path('analytics/', include('sims.analytics.urls')),
    path('notifications/', include('sims.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)