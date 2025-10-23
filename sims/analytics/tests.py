from __future__ import annotations

from datetime import date, timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from sims.analytics.services import TrendRequest, trend_for_user
from sims.logbook.models import LogbookEntry
from sims.users.models import User


class AnalyticsAPITests(APITestCase):
    def setUp(self) -> None:
        cache.clear()
        self.admin = User.objects.create_user(
            username="admin",
            password="testpass",
            role="admin",
            email="admin@example.com",
        )
        self.supervisor = User.objects.create_user(
            username="supervisor",
            password="testpass",
            role="supervisor",
            email="supervisor@example.com",
            specialty="surgery",
        )
        self.pg = User.objects.create_user(
            username="pg1",
            password="testpass",
            role="pg",
            email="pg1@example.com",
            specialty="surgery",
            year="1",
            supervisor=self.supervisor,
        )
        self.client.force_authenticate(self.admin)
        self._create_entries()

    def _create_entries(self) -> None:
        base_date = date(2024, 1, 1)
        for day_offset in range(5):
            LogbookEntry.objects.create(
                pg=self.pg,
                case_title=f"Case {day_offset}",
                date=base_date - timedelta(days=day_offset),
                location_of_activity="Ward",
                patient_history_summary="History",
                management_action="Action",
                topic_subtopic="Topic",
                status="approved" if day_offset % 2 == 0 else "pending",
                supervisor=self.supervisor,
                submitted_to_supervisor_at=timezone.now() - timedelta(days=day_offset),
                supervisor_action_at=timezone.now() - timedelta(days=max(day_offset - 1, 0)),
            )

    def test_trend_api_returns_data(self) -> None:
        url = reverse("analytics_api:trends")
        response = self.client.get(url, {"user_id": self.pg.pk, "window": 7})
        self.assertEqual(response.status_code, 200)
        payload = response.data
        self.assertEqual(payload["metric"], "entries")
        self.assertTrue(payload["series"])
        self.assertIn("moving_average", payload["series"][0])

    def test_comparative_api_requires_permission(self) -> None:
        url = reverse("analytics_api:comparative")
        response = self.client.get(
            url,
            {
                "primary_users": str(self.pg.pk),
                "secondary_users": str(self.pg.pk),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("primary", response.data)

        self.client.force_authenticate(self.pg)
        other_pg = User.objects.create_user(
            username="pg2",
            password="testpass",
            role="pg",
            email="pg2@example.com",
            specialty="surgery",
            year="1",
            supervisor=self.supervisor,
        )
        response = self.client.get(
            url,
            {
                "primary_users": str(other_pg.pk),
                "secondary_users": str(self.pg.pk),
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_performance_metrics_api(self) -> None:
        url = reverse("analytics_api:performance")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data["total_entries"], 0)

    def test_trend_service_caches_response(self) -> None:
        params = TrendRequest(window=7)
        cache_key = params.cache_key(self.pg.pk)
        self.assertIsNone(cache.get(cache_key))
        data = trend_for_user(self.admin, self.pg, params)
        cache_value = cache.get(cache_key)
        self.assertEqual(data, cache_value)

    def test_dashboard_overview_api(self) -> None:
        """Test dashboard overview endpoint."""
        url = reverse("analytics_api:dashboard-overview")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("total_residents", data)
        self.assertIn("active_rotations", data)
        self.assertIn("pending_certificates", data)
        self.assertIn("last_30d_logs", data)
        self.assertIn("last_30d_cases", data)
        self.assertIn("unverified_logs", data)

    def test_dashboard_trends_api(self) -> None:
        """Test dashboard trends endpoint."""
        url = reverse("analytics_api:dashboard-trends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("trends", data)
        self.assertIsInstance(data["trends"], list)

    def test_dashboard_compliance_api(self) -> None:
        """Test dashboard compliance endpoint."""
        url = reverse("analytics_api:dashboard-compliance")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("compliance", data)
        self.assertIsInstance(data["compliance"], list)
    
    def test_validate_window_invalid(self) -> None:
        """Test window validation with invalid values."""
        from sims.analytics.services import validate_window
        
        # Test invalid window value
        with self.assertRaises(ValueError) as cm:
            validate_window("15")  # Not in ALLOWED_WINDOWS
        self.assertIn("Window must be one of", str(cm.exception))
        
    def test_validate_window_none_defaults_to_30(self) -> None:
        """Test window validation with None defaults to 30."""
        from sims.analytics.services import validate_window
        self.assertEqual(validate_window(None), 30)
        
    def test_trend_for_user_permission_denied(self) -> None:
        """Test permission error when accessing other user's analytics."""
        params = TrendRequest(window=7)
        
        # PG trying to access another PG's data
        other_pg = User.objects.create_user(
            username="pg2",
            password="testpass",
            role="pg",
            email="pg2@example.com",
            specialty="surgery",
            year="1",
            supervisor=self.supervisor,
        )
        
        with self.assertRaises(PermissionError):
            trend_for_user(self.pg, other_pg, params)
    
    def test_trend_for_user_with_status_filter(self) -> None:
        """Test trend calculation with status filter."""
        params = TrendRequest(window=7)
        data = trend_for_user(self.admin, self.pg, params, status_filter=["approved"])
        
        self.assertIsNotNone(data)
        self.assertEqual(data["metric"], "entries")
        self.assertIn("series", data)
        
    def test_trend_for_user_no_entries(self) -> None:
        """Test trend for user with no logbook entries."""
        new_pg = User.objects.create_user(
            username="pg_new",
            password="testpass",
            role="pg",
            email="pgnew@example.com",
            specialty="surgery",
            year="1",
            supervisor=self.supervisor,
        )
        
        params = TrendRequest(window=7)
        data = trend_for_user(self.admin, new_pg, params)
        
        self.assertEqual(data["series"], [])
        self.assertEqual(data["window"], 7)
        self.assertEqual(data["metric"], "entries")
