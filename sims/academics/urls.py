from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"departments", views.DepartmentViewSet, basename="department")
router.register(r"batches", views.BatchViewSet, basename="batch")
router.register(r"students", views.StudentProfileViewSet, basename="studentprofile")

urlpatterns = [
    path("api/", include(router.urls)),
]
