#!/usr/bin/env python3
"""Create a tiny fake mbox for demos and agent checks."""

from __future__ import annotations

import mailbox
import sys
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path
from datetime import datetime, timezone


def make_message(sender: str, subject: str, body: str, day: int) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = "candidate@example.com"
    msg["Subject"] = subject
    msg["Date"] = format_datetime(datetime(2026, 5, day, 12, 0, tzinfo=timezone.utc))
    msg.set_content(body)
    return msg


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: make_sample_mbox.py /path/to/sample.mbox", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()

    box = mailbox.mbox(path)
    box.add(
        make_message(
            "Careers Team <noreply@examplecorp.com>",
            "Thank you for applying to ExampleCorp COOP Training",
            "تم استلام طلبك لبرنامج التدريب التعاوني. Track it here: https://careers.examplecorp.com/app/123",
            1,
        )
    )
    box.add(
        make_message(
            "Talent <jobs@futurebank.example>",
            "Action required for your graduate program application",
            "Please complete your assessment: https://futurebank.example/assessment",
            2,
        )
    )
    box.add(
        make_message(
            "طاقات <noreply@taqat.sa>",
            "تحديث على طلب برنامج تمهير",
            "نعتذر، لم تستوفِ شروط الأهلية للتدريب على رأس العمل.",
            3,
        )
    )
    box.add(
        make_message(
            "Friend <friend@example.net>",
            "Lunch?",
            "Are you free later today?",
            4,
        )
    )
    box.flush()
    box.close()
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
