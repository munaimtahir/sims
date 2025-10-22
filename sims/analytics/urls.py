"""URL routing for analytics APIs."""

from django.urls import path

from sims.analytics.views import (
    ComparativeAnalyticsView,
    PerformanceMetricsView,
    TrendAnalyticsView,
)

app_name = "analytics_api"

urlpatterns = [
    path("trends/", TrendAnalyticsView.as_view(), name="trends"),
    path("comparative/", ComparativeAnalyticsView.as_view(), name="comparative"),
    path("performance/", PerformanceMetricsView.as_view(), name="performance"),
]
