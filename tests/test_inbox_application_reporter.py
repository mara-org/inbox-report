from __future__ import annotations

import csv
import mailbox
import re
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path

import inbox_application_reporter as reporter


def make_message(
    sender: str,
    subject: str,
    body: str,
    date: str = "Fri, 01 May 2026 12:00:00 +0000",
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = "candidate@example.com"
    msg["Subject"] = subject
    msg["Date"] = date
    msg.set_content(body)
    return msg


APPLICATION_FIXTURES = [
    {
        "name": "greenhouse_received",
        "sender": "Greenhouse <no-reply@greenhouse.io>",
        "subject": "Your application to Data Intern at Northstar has been received",
        "body": "Thank you for applying. Your internship application has been received.",
        "application_type": "internship",
        "status": "submitted_or_received",
    },
    {
        "name": "lever_interview",
        "sender": "Lever <notifications@hire.lever.co>",
        "subject": "Interview invitation from Atlas Labs",
        "body": "We received your job application and would like to schedule an interview.",
        "application_type": "job",
        "status": "interview",
    },
    {
        "name": "workday_under_review",
        "sender": "Workday <noreply@myworkdayjobs.com>",
        "subject": "Application update from Workday",
        "body": "Your application for the graduate program is under review.",
        "application_type": "graduate_program",
        "status": "under_review",
    },
    {
        "name": "linkedin_submitted",
        "sender": "LinkedIn Jobs <jobs-noreply@linkedin.com>",
        "subject": "Your application was sent to ExampleCorp",
        "body": "Application submitted. The recruiter can now review your profile.",
        "application_type": "career_portal",
        "status": "submitted_or_received",
    },
    {
        "name": "smartrecruiters_action_required",
        "sender": "SmartRecruiters <noreply@smartrecruiters.com>",
        "subject": "Action required for your internship application",
        "body": "Please complete your application assessment before the deadline.",
        "application_type": "internship",
        "status": "action_required",
    },
    {
        "name": "saudi_coop_received",
        "sender": "Careers <noreply@careers.stc.com.sa>",
        "subject": "تم استلام طلب التدريب التعاوني",
        "body": "تم استلام طلبك لبرنامج التدريب التعاوني وسيتم التواصل معك لاحقا.",
        "application_type": "coop",
        "status": "submitted_or_received",
    },
    {
        "name": "tamheer_ineligible",
        "sender": "طاقات <noreply@taqat.sa>",
        "subject": "تحديث على طلب برنامج تمهير",
        "body": "نعتذر، لم تستوفِ شروط الأهلية للتدريب على رأس العمل.",
        "application_type": "tamheer",
        "status": "ineligible",
    },
    {
        "name": "arabic_interview",
        "sender": "فريق التوظيف <jobs@example.com.sa>",
        "subject": "دعوة للمقابلة الشخصية",
        "body": "تم ترشيحك للمقابلة الشخصية بخصوص طلب التوظيف.",
        "application_type": "job",
        "status": "interview",
    },
    {
        "name": "offer_letter",
        "sender": "Talent Acquisition <talent@futurebank.example>",
        "subject": "Offer letter for your job application",
        "body": "Congratulations, we are pleased to offer you the role.",
        "application_type": "job",
        "status": "offer_or_accepted",
    },
    {
        "name": "start_onboarding",
        "sender": "Recruiting <recruiting@cloudco.example>",
        "subject": "Your application onboarding details",
        "body": "Your job application is accepted. Your start date and onboarding steps are attached.",
        "application_type": "job",
        "status": "start_or_onboarding",
    },
    {
        "name": "closed_training",
        "sender": "Training Office <training@industry.example>",
        "subject": "COOP training application update",
        "body": "All training vacancies are filled for this term.",
        "application_type": "coop",
        "status": "closed_or_full",
    },
    {
        "name": "rejection",
        "sender": "Careers <careers@retail.example>",
        "subject": "Your job application",
        "body": "Unfortunately, you were not selected for this position.",
        "application_type": "job",
        "status": "rejected",
    },
]

NON_APPLICATION_FIXTURES = [
    {
        "name": "store_order",
        "sender": "Store <no-reply@shop.example>",
        "subject": "Order confirmation",
        "body": "Your order number 123 has been accepted and will be delivered soon.",
    },
    {
        "name": "social_job_digest",
        "sender": "Social Digest <digest@social.example>",
        "subject": 'People near you shared "وظائف شاغرة"',
        "body": "A social digest mentioning تدريب, وظيفة, and LinkedIn links.",
    },
    {
        "name": "newsletter",
        "sender": "Newsletter <news@tech.example>",
        "subject": "This week in early careers",
        "body": "A newsletter about career growth, not a candidate application.",
    },
    {
        "name": "terms_policy",
        "sender": "Account <legal@service.example>",
        "subject": "Terms and Privacy Policy - Copy for your records",
        "body": "These terms are applied to your account and this application.",
    },
    {
        "name": "course_marketing",
        "sender": "Language Lessons <hello@learning.example>",
        "subject": "Special offer to reach your goal",
        "body": "عرض خاص يساعدك تحقق هدفك وتطور لغتك اليوم.",
    },
    {
        "name": "game_coop_sale",
        "sender": "Game Store <offers@games.example>",
        "subject": "Co-op weekend sale",
        "body": "Play co-op games with a discount. No job, recruiter, or candidate workflow.",
    },
    {
        "name": "shipping_status",
        "sender": "Delivery <tracking@delivery.example>",
        "subject": "تحديث حالة طلبك",
        "body": "تم شحن طلبك وسيتم التوصيل خلال يومين.",
    },
]


class ReporterTests(unittest.TestCase):
    def test_application_fixture_pack(self) -> None:
        for fixture in APPLICATION_FIXTURES:
            with self.subTest(fixture=fixture["name"]):
                record = reporter.message_to_record(
                    make_message(fixture["sender"], fixture["subject"], fixture["body"])
                )

                self.assertIsNotNone(record)
                assert record is not None
                self.assertEqual(record.application_type, fixture["application_type"])
                self.assertEqual(record.status, fixture["status"])

    def test_non_application_fixture_pack(self) -> None:
        for fixture in NON_APPLICATION_FIXTURES:
            with self.subTest(fixture=fixture["name"]):
                record = reporter.message_to_record(
                    make_message(fixture["sender"], fixture["subject"], fixture["body"])
                )

                self.assertIsNone(record)

    def test_detects_application_email(self) -> None:
        msg = make_message(
            "Careers Team <noreply@examplecorp.com>",
            "Thank you for applying to ExampleCorp COOP Training",
            "تم استلام طلبك لبرنامج التدريب التعاوني. Track: https://careers.examplecorp.com/app/123",
        )

        record = reporter.message_to_record(msg)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.organization_guess, "Examplecorp")
        self.assertEqual(record.application_type, "coop")
        self.assertEqual(record.status, "submitted_or_received")
        self.assertEqual(record.confidence, "high")
        self.assertEqual(record.review_bucket, "auto_classified")
        self.assertIn("https://careers.examplecorp.com/app/123", record.links)

    def test_extracts_application_reference_numbers(self) -> None:
        msg = make_message(
            "System <system@successfactors.eu>",
            "PwC Careers: Thank you for your Application",
            (
                "Thank you for applying to PwC Middle East. "
                "Job Requisition: 10162. "
                "View your application at https://example.test/?fbja_appId=368303"
            ),
        )

        record = reporter.message_to_record(msg)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertIn("Job Requisition 10162", record.application_reference)
        self.assertIn("Application ID 368303", record.application_reference)

    def test_extracts_arabic_application_reference_number(self) -> None:
        msg = make_message(
            "Recruiting <jobs@example.com.sa>",
            "تم استلام طلب التدريب التعاوني",
            "تم استلام طلبك لبرنامج التدريب التعاوني. رقم الطلب: 987654.",
        )

        record = reporter.message_to_record(msg)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertIn("987654", record.application_reference)

    def test_platform_sender_uses_real_company_from_body(self) -> None:
        msg = make_message(
            "Workday <noreply@myworkdayjobs.com>",
            "Application update",
            "Thanks for applying for the role of Data Intern at Northstar. Your application will be reviewed.",
        )

        record = reporter.message_to_record(msg)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.organization_guess, "Northstar")

    def test_filters_records_after_date_and_excluded_org(self) -> None:
        old_msg = make_message(
            "Careers <jobs@oldco.example>",
            "Application received",
            "Thank you for applying to our internship.",
            date="Wed, 31 Dec 2025 12:00:00 +0000",
        )
        kept_msg = make_message(
            "Careers <jobs@keepco.example>",
            "Application received",
            "Thank you for applying to our internship.",
            date="Thu, 01 Jan 2026 12:00:00 +0000",
        )
        excluded_msg = make_message(
            "Careers <jobs@skipco.example>",
            "Application received",
            "Thank you for applying to our internship.",
            date="Fri, 02 Jan 2026 12:00:00 +0000",
        )
        records = [
            record
            for record in (
                reporter.message_to_record(old_msg),
                reporter.message_to_record(kept_msg),
                reporter.message_to_record(excluded_msg),
            )
            if record is not None
        ]

        filtered = reporter.filter_records(
            records,
            after=reporter.parse_filter_date("2026-01-01"),
            exclude_orgs=["Skipco"],
        )

        self.assertEqual([record.organization_guess for record in filtered], ["Keepco"])

    def test_ignores_regular_email(self) -> None:
        msg = make_message(
            "Friend <friend@example.net>",
            "Lunch?",
            "Are you free later today?",
        )

        self.assertIsNone(reporter.message_to_record(msg))

    def test_ignores_social_job_news_digest(self) -> None:
        msg = make_message(
            "Twitter <info@twitter.com>",
            'People in Riyadh shared "هيئة السوق المالية تعلن وظائف إدارية وتقنية"',
            "What's happening وظائف اليوم تدريب هدف linkedin.com",
        )

        self.assertIsNone(reporter.message_to_record(msg))

    def test_ignores_store_order_status(self) -> None:
        msg = make_message(
            "Store <no-reply@salla.sa>",
            "نبشرك بتأكيد الطلب",
            "تم إكمال طلبك بنجاح. رقم الطلب 12345 والدفع عند الاستلام.",
        )

        self.assertIsNone(reporter.message_to_record(msg))

    def test_ignores_goal_or_offer_marketing_without_application_context(self) -> None:
        msg = make_message(
            "Language Lessons <hello@learning.example>",
            "Special offer to reach your goal",
            "عرض خاص يساعدك تحقق هدفك وتطور لغتك اليوم.",
        )

        self.assertIsNone(reporter.message_to_record(msg))

    def test_include_weak_returns_noisy_audit_candidate(self) -> None:
        msg = make_message(
            "Twitter <info@twitter.com>",
            'People in Riyadh shared "وظائف شاغرة"',
            "A social digest with تدريب and linkedin.com links.",
        )

        self.assertIsNone(reporter.message_to_record(msg))
        weak_record = reporter.message_to_record(msg, include_weak=True)

        self.assertIsNotNone(weak_record)
        assert weak_record is not None
        self.assertEqual(weak_record.review_bucket, "needs_review")

    def test_ignores_terms_email_with_generic_application_words(self) -> None:
        msg = make_message(
            "PlayStation Network <no-reply@email.sonyentertainmentnetwork.com>",
            "Terms and Privacy Policy - Copy for your records",
            "These terms are applied to your account and this application.",
        )

        self.assertIsNone(reporter.message_to_record(msg))

    def test_detects_linkedin_application_confirmation(self) -> None:
        msg = make_message(
            "LinkedIn Jobs <jobs-noreply@linkedin.com>",
            "Your application was sent to ExampleCorp",
            "Application submitted. The recruiter can now review your profile.",
        )

        record = reporter.message_to_record(msg)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.status, "submitted_or_received")
        self.assertEqual(record.review_bucket, "auto_classified")

    def test_does_not_match_intern_inside_international(self) -> None:
        msg = make_message(
            "Newsletter <news@example.net>",
            "International conference update",
            "A note about international travel and nothing about training.",
        )

        self.assertIsNone(reporter.message_to_record(msg))

    def test_writes_csv_html_and_summary(self) -> None:
        msg = make_message(
            "Talent <jobs@futurebank.example>",
            "Action required for your graduate program application",
            "Please complete your assessment: https://futurebank.example/assessment",
        )
        record = reporter.message_to_record(msg)
        self.assertIsNotNone(record)
        records = [record]
        summary_rows = reporter.build_summary(records)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            details = tmp_path / "nested" / "applications.csv"
            html = tmp_path / "nested" / "report.html"
            reporter.write_csv(
                details,
                [records[0].__dict__],
                list(reporter.ApplicationEmail.__dataclass_fields__.keys()),
            )
            reporter.write_html_report(html, records, summary_rows)

            self.assertTrue(details.exists())
            self.assertTrue(html.exists())
            with details.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["application_type"], "graduate_program")
            self.assertEqual(rows[0]["status"], "action_required")
            self.assertEqual(rows[0]["review_bucket"], "needs_review")
            self.assertIn("Futurebank", html.read_text(encoding="utf-8"))

    def test_can_hide_status_and_links_in_outputs(self) -> None:
        msg = make_message(
            "Talent <jobs@futurebank.example>",
            "Action required for your graduate program application",
            "Please complete your assessment: https://futurebank.example/assessment",
        )
        record = reporter.message_to_record(msg)
        self.assertIsNotNone(record)
        records = [record]
        summary_rows = reporter.build_summary(records, hide_status=True)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            details = tmp_path / "applications.csv"
            html = tmp_path / "report.html"
            reporter.write_csv(
                details,
                [
                    reporter.record_to_row(
                        records[0],
                        friendly_labels=True,
                        hide_status=True,
                        hide_links=True,
                    )
                ],
                reporter.detail_fieldnames(hide_status=True, hide_links=True),
            )
            reporter.write_html_report(
                html,
                records,
                summary_rows,
                title="Application Report",
                hide_status=True,
                hide_links=True,
                friendly_labels=True,
            )

            with details.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
            self.assertNotIn("status", rows[0])
            self.assertNotIn("links", rows[0])
            html_text = html.read_text(encoding="utf-8")
            self.assertIn("<h1>Application Report</h1>", html_text)
            self.assertNotIn("<th>Status</th>", html_text)
            self.assertNotIn("<th>Links</th>", html_text)

    def test_reads_mbox_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mbox_path = Path(tmp) / "mail.mbox"
            box = mailbox.mbox(mbox_path)
            box.add(
                make_message(
                    "Careers <noreply@examplecorp.com>",
                    "Application received",
                    "Thank you for applying to our COOP training program.",
                )
            )
            box.add(make_message("Friend <friend@example.net>", "Lunch?", "Free later?"))
            box.flush()
            box.close()

            records = reporter.read_application_records(mbox_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].application_type, "coop")

    def test_reads_apple_mail_mbox_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_path = Path(tmp) / "Inbox.mbox"
            package_path.mkdir()
            box = mailbox.mbox(package_path / "mbox")
            box.add(
                make_message(
                    "Careers <noreply@examplecorp.com>",
                    "Application received",
                    "Thank you for applying to our COOP training program.",
                )
            )
            box.flush()
            box.close()

            records = reporter.read_application_records(package_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].application_type, "coop")

    def test_reads_google_takeout_mail_folder_with_mbox_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mail_dir = Path(tmp) / "Takeout" / "Mail"
            mail_dir.mkdir(parents=True)
            mbox_path = mail_dir / "All mail Including Spam and Trash.mbox"
            box = mailbox.mbox(mbox_path)
            box.add(
                make_message(
                    "Careers <noreply@aramco.com>",
                    "Application received - COOP Training Program",
                    "Your COOP training application was received.",
                )
            )
            box.add(make_message("Friend <friend@example.net>", "Lunch?", "Free later?"))
            box.flush()
            box.close()

            records = reporter.read_application_records(mail_dir)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].organization_guess, "Aramco")
        self.assertEqual(records[0].application_type, "coop")

    def test_reads_eml_file_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            eml_path = Path(tmp) / "message.eml"
            msg = make_message(
                "Hadaf <noreply@hrdf.org.sa>",
                "Tamheer application update",
                "Your Tamheer on-the-job training application is under review.",
            )
            eml_path.write_bytes(msg.as_bytes())

            records = reporter.read_application_records(eml_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].application_type, "tamheer")
        self.assertEqual(records[0].status, "under_review")

    def test_reads_eml_directory_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            eml_dir = Path(tmp) / "outlook-export"
            eml_dir.mkdir()
            (eml_dir / "application.eml").write_bytes(
                make_message(
                    "Recruiting <jobs@company.example>",
                    "Interview invitation",
                    "We received your job application and would like to schedule an interview.",
                ).as_bytes()
            )
            (eml_dir / "regular.eml").write_bytes(
                make_message("Friend <friend@example.net>", "Coffee", "See you.").as_bytes()
            )

            records = reporter.read_application_records(eml_dir)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, "interview")

    def test_cli_aliases_and_output_defaults_follow_out_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out = tmp_path / "reports" / "details.csv"
            html = tmp_path / "custom.html"
            pdf = tmp_path / "custom.pdf"

            args = reporter.parse_args(
                [
                    "/tmp/mail.mbox",
                    "--output",
                    str(out),
                    "--html",
                    str(html),
                    "--pdf",
                    str(pdf),
                    "--after",
                    "2026-01-01",
                    "--exclude-org",
                    "Y Combinator",
                    "--title",
                    "Application Report",
                    "--hide-status",
                    "--hide-links",
                    "--friendly-labels",
                    "--include-low-confidence",
                    "--quiet",
                ]
            )

        self.assertEqual(args.out, out)
        self.assertEqual(args.summary_out, out.parent / "applications_summary.csv")
        self.assertEqual(args.html_out, html)
        self.assertEqual(args.pdf_out, pdf)
        self.assertEqual(args.after, reporter.parse_filter_date("2026-01-01"))
        self.assertEqual(args.exclude_org, ["Y Combinator"])
        self.assertEqual(args.title, "Application Report")
        self.assertTrue(args.hide_status)
        self.assertTrue(args.hide_links)
        self.assertTrue(args.friendly_labels)
        self.assertTrue(args.include_weak)
        self.assertTrue(args.quiet)

    def test_directory_without_supported_files_gives_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            empty_package = Path(tmp) / "Inbox.mbox"
            empty_package.mkdir()

            with self.assertRaisesRegex(ValueError, "does not look like"):
                list(reporter.iter_input_messages(empty_package))

    def test_pst_input_gives_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pst_path = Path(tmp) / "mail.pst"
            pst_path.write_bytes(b"not a real pst")

            with self.assertRaisesRegex(ValueError, "PST files are not parsed directly"):
                list(reporter.iter_input_messages(pst_path))

    def test_pyproject_version_matches_module(self) -> None:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        match = re.search(r'^version = "([^"]+)"$', text, re.MULTILINE)
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.group(1), reporter.VERSION)
        self.assertIn('inbox-report = "inbox_application_reporter:main"', text)

    def test_saudi_domain_guess_handles_com_sa(self) -> None:
        self.assertEqual(reporter.org_from_domain("careers.stc.com.sa"), "Stc")
        self.assertEqual(reporter.org_from_domain("jobs.hrdf.org.sa"), "Hrdf")

    def test_saudi_status_terms(self) -> None:
        msg = make_message(
            "طاقات <noreply@taqat.sa>",
            "تحديث على طلب برنامج تمهير",
            "نعتذر، لم تستوفِ شروط الأهلية للتدريب على رأس العمل.",
        )

        record = reporter.message_to_record(msg)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.application_type, "tamheer")
        self.assertEqual(record.status, "ineligible")
        self.assertEqual(record.review_bucket, "auto_classified")
        self.assertIn("تمهير", record.matched_terms)


if __name__ == "__main__":
    unittest.main()
