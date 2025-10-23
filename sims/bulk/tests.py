from __future__ import annotations

import csv
import io
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from sims.bulk.models import BulkOperation
from sims.bulk.services import BulkService
from sims.logbook.models import LogbookEntry
from sims.users.models import User


class BulkOperationTests(APITestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_user(username="admin", password="testpass", role="admin")
        self.supervisor = User.objects.create_user(
            username="sup",
            password="testpass",
            role="supervisor",
            specialty="surgery",
        )
        self.pg = User.objects.create_user(
            username="pg",
            password="testpass",
            role="pg",
            specialty="surgery",
            year="1",
            supervisor=self.supervisor,
        )
        self.client.force_authenticate(self.admin)
        self.entries = [
            LogbookEntry.objects.create(
                pg=self.pg,
                case_title=f"Case {i}",
                date=date(2024, 1, 1),
                location_of_activity="Ward",
                patient_history_summary="History",
                management_action="Action",
                topic_subtopic="Topic",
            )
            for i in range(3)
        ]

    def test_bulk_review_service(self) -> None:
        service = BulkService(self.admin, chunk_size=2)
        operation = service.review_entries([entry.pk for entry in self.entries], status="approved")
        self.assertEqual(operation.status, BulkOperation.STATUS_COMPLETED)
        self.assertEqual(operation.success_count, 3)
        self.assertEqual(LogbookEntry.objects.filter(status="approved").count(), 3)

    def test_bulk_assignment_api(self) -> None:
        url = reverse("bulk_api:assignment")
        payload = {
            "entry_ids": [entry.pk for entry in self.entries],
            "supervisor_id": self.supervisor.pk,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            LogbookEntry.objects.filter(supervisor=self.supervisor).count(),
            len(self.entries),
        )

    def test_bulk_import_dry_run(self) -> None:
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(
            csv_buffer, fieldnames=["pg_username", "case_title", "date", "status"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "pg_username": self.pg.username,
                "case_title": "Imported Case",
                "date": date(2024, 1, 1).isoformat(),
                "status": "pending",
            }
        )
        writer.writerow(
            {
                "pg_username": "unknown",
                "case_title": "Bad Case",
                "date": date(2024, 1, 1).isoformat(),
                "status": "pending",
            }
        )
        uploaded = SimpleUploadedFile(
            "import.csv", csv_buffer.getvalue().encode("utf-8"), content_type="text/csv"
        )
        url = reverse("bulk_api:import")
        response = self.client.post(
            url, {"file": uploaded, "dry_run": True, "allow_partial": False}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["failure_count"], 1)
        self.assertEqual(LogbookEntry.objects.filter(case_title="Imported Case").count(), 0)

        uploaded = SimpleUploadedFile(
            "import.csv", csv_buffer.getvalue().encode("utf-8"), content_type="text/csv"
        )
        response = self.client.post(
            url, {"file": uploaded, "dry_run": False, "allow_partial": True}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LogbookEntry.objects.filter(case_title="Imported Case").count(), 1)

    def test_bulk_review_with_invalid_ids(self) -> None:
        """Test bulk review with some invalid IDs"""
        service = BulkService(self.admin, chunk_size=2)
        valid_ids = [entry.pk for entry in self.entries[:2]]
        invalid_ids = [9999, 10000]
        all_ids = valid_ids + invalid_ids
        
        operation = service.review_entries(all_ids, status="approved")
        self.assertEqual(operation.status, BulkOperation.STATUS_COMPLETED)
        self.assertEqual(operation.success_count, 2)
        self.assertEqual(operation.failure_count, 2)
        
    def test_bulk_assignment_with_invalid_ids(self) -> None:
        """Test bulk assignment with some invalid IDs"""
        service = BulkService(self.admin, chunk_size=2)
        valid_ids = [entry.pk for entry in self.entries[:1]]
        invalid_ids = [9999]
        all_ids = valid_ids + invalid_ids
        
        operation = service.assign_supervisor(all_ids, self.supervisor)
        self.assertEqual(operation.status, BulkOperation.STATUS_COMPLETED)
        self.assertEqual(operation.success_count, 1)
        self.assertEqual(operation.failure_count, 1)
        
    def test_bulk_import_missing_columns(self) -> None:
        """Test CSV import with missing required columns"""
        csv_buffer = io.StringIO()
        # Missing 'date' and 'status' columns
        writer = csv.DictWriter(csv_buffer, fieldnames=["pg_username", "case_title"])
        writer.writeheader()
        writer.writerow({"pg_username": self.pg.username, "case_title": "Test"})
        
        uploaded = SimpleUploadedFile(
            "import.csv", csv_buffer.getvalue().encode("utf-8"), content_type="text/csv"
        )
        url = reverse("bulk_api:import")
        response = self.client.post(url, {"file": uploaded, "dry_run": True})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing columns", str(response.data))
        
    def test_bulk_import_unsupported_format(self) -> None:
        """Test import with unsupported file format"""
        uploaded = SimpleUploadedFile(
            "import.txt", b"random text content", content_type="text/plain"
        )
        url = reverse("bulk_api:import")
        response = self.client.post(url, {"file": uploaded, "dry_run": True})
        self.assertEqual(response.status_code, 400)
        
    def test_permission_denied_for_pg_user(self) -> None:
        """Test that PG users cannot perform bulk operations"""
        from django.core.exceptions import PermissionDenied
        with self.assertRaises(PermissionDenied):
            BulkService(self.pg, chunk_size=2)
