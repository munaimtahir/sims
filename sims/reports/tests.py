from __future__ import annotations

import base64
import io
from datetime import date, timedelta

from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook
from rest_framework.test import APITestCase

from sims.logbook.models import LogbookEntry
from sims.reports.models import ReportTemplate, ScheduledReport
from sims.reports.services import ReportService
from sims.users.models import User


class ReportingTests(APITestCase):
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
        LogbookEntry.objects.create(
            pg=self.pg,
            case_title="Report Case",
            date=date(2024, 1, 1),
            location_of_activity="Ward",
            patient_history_summary="History",
            management_action="Action",
            topic_subtopic="Topic",
            status="approved",
            supervisor=self.supervisor,
        )
        self.template, _ = ReportTemplate.objects.get_or_create(
            slug="logbook-summary",
            defaults={
                "name": "Logbook Summary",
                "template_name": "reports/logbook_summary.html",
            },
        )

    def test_service_generates_pdf_and_excel(self) -> None:
        service = ReportService(self.admin)
        pdf_report = service.generate(self.template, {"format": "pdf"}, "pdf")
        self.assertTrue(pdf_report.content.startswith(b"%PDF"))

        excel_report = service.generate(self.template, {"format": "xlsx"}, "xlsx")
        workbook = load_workbook(io.BytesIO(excel_report.content))
        sheet = workbook.active
        self.assertEqual(sheet.cell(row=2, column=4).value, "Report Case")

    def test_generate_api_returns_base64(self) -> None:
        url = reverse("reports_api:generate")
        response = self.client.post(
            url,
            {"template_slug": self.template.slug, "format": "pdf", "params": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        decoded = base64.b64decode(response.data["content"])
        self.assertTrue(decoded.startswith(b"%PDF"))

    def test_scheduled_report_runner(self) -> None:
        schedule = ScheduledReport.objects.create(
            template=self.template,
            created_by=self.admin,
            email_to="admin@example.com",
            params={"format": "pdf"},
            cron="0 6 * * *",
            next_run_at=timezone.now(),
        )
        call_command("run_scheduled_reports")
        schedule.refresh_from_db()
        self.assertIsNotNone(schedule.last_run_at)
        self.assertTrue(schedule.last_result.get("success"))
