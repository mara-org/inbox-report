#!/usr/bin/env python3
"""Turn an mbox export into application reports.

No inbox login. No sending. No cloud. Just a local export going in and tidy
CSV/HTML/PDF files coming out.
"""

from __future__ import annotations

import argparse
import csv
import html
import mailbox
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.parser import BytesParser
from email.policy import default
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path
from typing import Iterable, Iterator, Sequence


VERSION = "1.0.1"

APPLICATION_TERMS = [
    "training opportunity",
    "training application",
    "on-the-job training",
    "internship",
    "intern",
    "trainee",
    "co-op",
    "co-op training",
    "coop",
    "coop training",
    "cooperative training",
    "cooperative education",
    "coop program",
    "co-op program",
    "coop opportunity",
    "co-op opportunity",
    "coop application",
    "co-op application",
    "coop training letter",
    "official coop training letter",
    "field training",
    "practical training",
    "summer training",
    "university training",
    "university training letter",
    "graduation requirement",
    "final-year student",
    "final year student",
    "graduate program",
    "graduate development",
    "graduate development program",
    "tamheer",
    "taqat",
    "jadarat",
    "hrdf",
    "hadaf",
    "early careers",
    "career",
    "careers",
    "application",
    "applied",
    "candidate",
    "interview",
    "interview invitation",
    "offer letter",
    "nominated by your university",
    "nominated by the university",
    "job application",
    "thank you for applying",
    "received your application",
    "your application",
    "application request",
    "تدريب",
    "تعاوني",
    "تعاونية",
    "تدريب تعاوني",
    "التدريب التعاوني",
    "برنامج التدريب التعاوني",
    "متدرب تعاوني",
    "تدريب ميداني",
    "التدريب الميداني",
    "تدريب عملي",
    "التدريب العملي",
    "تدريب صيفي",
    "التدريب الصيفي",
    "فرصة تدريب",
    "فرصة تدريبية",
    "فرص تدريبية",
    "عرض تدريبي",
    "عرض فرصة تدريبية",
    "طلب تدريب",
    "طلب التقديم",
    "طلب الالتحاق",
    "متطلب تخرج",
    "متطلبات التخرج",
    "خطاب تدريب",
    "خطاب التدريب",
    "خطاب تدريب تعاوني",
    "إفادة التدريب",
    "افادة التدريب",
    "نموذج مباشرة",
    "نموذج المباشرة",
    "التدريب على رأس العمل",
    "تدريب على رأس العمل",
    "برنامج تمهير",
    "تمهير",
    "طاقات",
    "جدارات",
    "هدف",
    "صندوق تنمية الموارد البشرية",
    "حديث التخرج",
    "حديثي التخرج",
    "خريج",
    "الخريجين",
    "متدرب",
    "طلبك",
    "تقديمك",
    "تم استلام طلبك",
    "شكرا لتقديمك",
    "شكراً لتقديمك",
    "بوابة التوظيف",
    "وظيفة",
    "الوظيفة",
    "مرشح",
    "ترشيح",
    "تم ترشيحك",
    "مقابلة",
    "المقابلة",
    "دعوة للمقابلة",
    "عرض وظيفي",
]

DIRECT_APPLICATION_TERMS = [
    "thank you for applying",
    "thanks for applying",
    "received your application",
    "we received your application",
    "application received",
    "your application has been received",
    "application was received",
    "application submitted",
    "successfully submitted",
    "your application was submitted",
    "your application",
    "job application",
    "training application",
    "coop application",
    "co-op application",
    "tamheer application",
    "internship application",
    "graduate program application",
    "interview invitation",
    "invited to interview",
    "candidate application",
    "candidate profile",
    "offer letter",
    "تم استلام طلبك",
    "استلام طلبك",
    "شكرا لتقديمك",
    "شكراً لتقديمك",
    "تم تقديم الطلب",
    "تم تقديم الطلب بنجاح",
    "تم إرسال طلبك",
    "تم ارسال طلبك",
    "طلب التوظيف",
    "طلب التدريب",
    "طلب برنامج تمهير",
    "طلب برنامج التدريب",
    "طلب التدريب التعاوني",
    "دعوة للمقابلة",
    "تم قبولك",
    "تم اختيارك",
    "تم ترشيحك",
]

APPLICATION_CONTEXT_TERMS = [
    "applying",
    "applied for",
    "candidate",
    "recruiter",
    "recruiting",
    "recruitment",
    "talent acquisition",
    "complete your application",
    "complete your profile",
    "assessment",
    "screening",
    "interview",
    "under review",
    "eligibility",
    "not eligible",
    "ineligible",
    "onboarding",
    "joining date",
    "start date",
    "تقديمك",
    "طلبك الوظيفي",
    "مرشح",
    "ترشيح",
    "المقابلة",
    "قيد المراجعة",
    "تحت المراجعة",
    "الأهلية",
    "الاهلية",
    "غير مؤهل",
    "شروط الأهلية",
    "شروط الاهلية",
    "مباشرة",
]

ROLE_CONTEXT_TERMS = [
    "co-op training",
    "coop training",
    "cooperative training",
    "cooperative education",
    "tamheer",
    "on-the-job training",
    "internship",
    "graduate program",
    "graduate development program",
    "field training",
    "practical training",
    "university training",
    "التدريب التعاوني",
    "برنامج التدريب التعاوني",
    "تدريب تعاوني",
    "متدرب تعاوني",
    "تمهير",
    "التدريب على رأس العمل",
    "تدريب على رأس العمل",
    "تدريب ميداني",
    "التدريب الميداني",
    "تدريب عملي",
    "التدريب العملي",
    "فرصة تدريبية",
    "متطلب تخرج",
    "متطلبات التخرج",
]

NON_APPLICATION_TERMS = [
    "people in riyadh shared",
    "what's happening",
    "your highlights",
    "tweeted",
    "retweeted",
    "shared a link",
    "not a candidate application",
    "not an application",
    "not a job application",
    "terms and privacy policy",
    "terms of service",
    "privacy policy",
    "copy for your records",
    "free games",
    "sweet summer deals",
    "new rewards",
    "newsletter",
    "your order",
    "order number",
    "order confirmation",
    "order status",
    "invoice",
    "receipt",
    "shipping",
    "delivery",
    "delivered",
    "checkout",
    "cart",
    "payment",
    "refund",
    "coupon",
    "discount",
    "فاتورة",
    "تأكيد الطلب",
    "تاكيد الطلب",
    "تحديث حالة الطلب",
    "تحديث حالة طلبك",
    "تحديث حالة طلب",
    "تم إكمال طلبك",
    "تم اكمال طلبك",
    "ضمان تسليم",
    "تسليم طلبك",
    "رقم الطلب",
    "الشحن",
    "التوصيل",
    "الدفع",
    "السلة",
    "سلة التسوق",
    "نفاد الكمية",
    "كوبون",
    "خصم",
]

RECRUITING_SENDER_TERMS = [
    "career",
    "careers",
    "job",
    "jobs",
    "recruiting",
    "recruitment",
    "talent",
    "hr",
]

ATS_TERMS = [
    "greenhouse",
    "lever",
    "workday",
    "taleo",
    "successfactors",
    "smartrecruiters",
    "jobvite",
    "oraclecloud",
    "brassring",
    "icims",
    "ashbyhq",
    "bamboohr",
    "linkedin",
    "indeed",
    "taqat",
    "jadarat",
    "tamheer",
    "hrdf",
    "hadaf",
    "careers.stc.com.sa",
    "jobs.sabic.com",
]

STATUS_PATTERNS = [
    (
        "offer_or_accepted",
        [
            "training opportunity offer",
            "offer",
            "congratulations",
            "selected",
            "accepted",
            "تهانينا",
            "مبروك",
            "قبول",
            "تم قبول",
            "تم قبولك",
            "تم اختيارك",
            "تم ترشيحك",
            "عرض تدريبي",
            "عرض فرصة تدريبية",
            "فرصة تدريبية لك",
        ],
    ),
    (
        "start_or_onboarding",
        [
            "start date",
            "joining date",
            "onboarding",
            "commencement",
            "باشر",
            "مباشرة",
            "المباشرة",
            "تاريخ المباشرة",
            "بدء التدريب",
            "بدء البرنامج",
            "انضمام",
            "نموذج مباشرة",
            "نموذج المباشرة",
        ],
    ),
    (
        "interview",
        [
            "interview",
            "interview invitation",
            "assessment center",
            "phone screen",
            "phone interview",
            "مقابلة",
            "المقابلة",
            "المقابلة الهاتفية",
            "المقابلة الشخصية",
            "دعوة للمقابلة",
        ],
    ),
    (
        "ineligible",
        [
            "not eligible",
            "ineligible",
            "did not meet the eligibility",
            "غير مؤهل",
            "غير مؤهلة",
            "لم تستوف",
            "لم تستوفي",
            "لم تستوفِ",
            "معايير الأهلية",
            "شروط الأهلية",
        ],
    ),
    (
        "rejected",
        [
            "unfortunately",
            "not selected",
            "regret to inform",
            "لن نتمكن",
            "نعتذر",
            "لم يتم اختيارك",
            "رفض",
            "مرفوض",
            "تم رفض",
        ],
    ),
    (
        "closed_or_full",
        [
            "no vacancies",
            "all vacancies are filled",
            "all training vacancies are filled",
            "all training vacancies are occupied",
            "closed",
            "اكتمل العدد",
            "اكتمال العدد",
            "جميع الشواغر التدريبية مشغولة",
            "الشواغر التدريبية مشغولة",
            "تم إغلاق",
            "تم اغلاق",
        ],
    ),
    (
        "action_required",
        [
            "complete your application",
            "complete your profile",
            "upload",
            "attach",
            "assessment",
            "test",
            "login",
            "sign in",
            "action required",
            "additional information",
            "استكمال",
            "اكمال",
            "إكمال",
            "أكمل",
            "استكمل",
            "إرفاق",
            "ارفاق",
            "رفع",
            "اختبار",
            "اضغط",
            "سجل دخول",
            "تسجيل الدخول",
            "الملف الشخصي",
            "شهادة التخرج",
            "المؤهل",
        ],
    ),
    (
        "under_review",
        [
            "under review",
            "being reviewed",
            "will be reviewed",
            "verification",
            "قيد المراجعة",
            "تحت المراجعة",
            "جاري التحقق",
        ],
    ),
    (
        "submitted_or_received",
        [
            "thank you for applying",
            "received your application",
            "application received",
            "application submitted",
            "successfully submitted",
            "your application was sent",
            "your application was submitted",
            "request submitted",
            "تم استلام طلبك",
            "استلام طلبك",
            "شكرا لتقديمك",
            "شكراً لتقديمك",
            "تم تقديم",
            "تم تقديم الطلب",
            "تم تقديم الطلب بنجاح",
            "تم إرسال طلبك",
            "تم ارسال طلبك",
        ],
    ),
]

GENERIC_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "icloud.com",
    "yahoo.com",
    "linkedin.com",
    "indeed.com",
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "workday.com",
    "successfactors.com",
    "smartrecruiters.com",
    "jobvite.com",
    "oraclecloud.com",
    "brassring.com",
    "icims.com",
    "ashbyhq.com",
    "bamboohr.com",
}

SAUDI_DOMAIN_SUFFIXES = (
    "com.sa",
    "edu.sa",
    "gov.sa",
    "org.sa",
    "net.sa",
    "med.sa",
    "sch.sa",
)

COMMON_HOST_PREFIXES = {
    "apply",
    "career",
    "careers",
    "email",
    "hr",
    "jobs",
    "mail",
    "notification",
    "notifications",
    "noreply",
    "recruiting",
    "recruitment",
    "talent",
}

GENERIC_ARABIC_SENDER_WORDS = [
    "برنامج التدريب التعاوني",
    "التدريب التعاوني",
    "برنامج تمهير",
    "التدريب",
    "التعاوني",
    "التوظيف",
    "الموارد البشرية",
    "فريق",
    "برنامج",
]

HIGH_SIGNAL_TERMS = [
    "thank you for applying",
    "received your application",
    "application received",
    "application submitted",
    "your application was sent",
    "your application was submitted",
    "successfully submitted",
    "cooperative training",
    "coop training",
    "co-op training",
    "tamheer",
    "on-the-job training",
    "training opportunity",
    "graduation requirement",
    "التدريب التعاوني",
    "برنامج التدريب التعاوني",
    "تدريب تعاوني",
    "تمهير",
    "التدريب على رأس العمل",
    "فرصة تدريبية",
    "تم استلام طلبك",
    "تم تقديم الطلب",
]

APPLICATION_TYPE_PATTERNS = [
    (
        "tamheer",
        [
            "tamheer",
            "taqat",
            "jadarat",
            "hrdf",
            "hadaf",
            "on-the-job training",
            "graduate development",
            "graduate development program",
            "تمهير",
            "طاقات",
            "جدارات",
            "هدف",
            "التدريب على رأس العمل",
            "تدريب على رأس العمل",
            "صندوق تنمية الموارد البشرية",
        ],
    ),
    (
        "coop",
        [
            "co-op",
            "co-op training",
            "coop",
            "coop training",
            "cooperative training",
            "cooperative education",
            "coop program",
            "co-op program",
            "graduation requirement",
            "university training letter",
            "التدريب التعاوني",
            "برنامج التدريب التعاوني",
            "تدريب تعاوني",
            "متدرب تعاوني",
            "خطاب تدريب تعاوني",
            "متطلب تخرج",
            "متطلبات التخرج",
        ],
    ),
    (
        "internship",
        [
            "internship",
            "intern",
            "summer training",
            "تدريب صيفي",
            "التدريب الصيفي",
        ],
    ),
    (
        "graduate_program",
        [
            "graduate program",
            "early careers",
            "fresh graduate",
            "حديث التخرج",
            "حديثي التخرج",
            "خريج",
            "الخريجين",
        ],
    ),
    (
        "job",
        [
            "job application",
            "طلب التوظيف",
            "career",
            "careers",
            "وظيفة",
            "الوظيفة",
            "بوابة التوظيف",
        ],
    ),
    (
        "training",
        [
            "training opportunity",
            "training application",
            "field training",
            "practical training",
            "university training",
            "تدريب ميداني",
            "التدريب الميداني",
            "تدريب عملي",
            "التدريب العملي",
            "فرصة تدريب",
            "فرصة تدريبية",
            "فرص تدريبية",
            "طلب تدريب",
        ],
    ),
]

URL_RE = re.compile(r"https?://[^\s<>\")\]]+", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
RTL_RE = re.compile(r"[\u0600-\u06FF]")

PDF_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/Library/Fonts/Arial.ttf",
]

PDF_BOLD_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


@dataclass
class ApplicationEmail:
    date: str
    sender_name: str
    sender_email: str
    sender_domain: str
    organization_guess: str
    subject: str
    application_type: str
    status: str
    confidence: str
    review_bucket: str
    matched_terms: str
    links: str
    snippet: str


def decode_mime(value: str | None) -> str:
    if not value:
        return ""

    parts: list[str] = []
    for payload, encoding in decode_header(value):
        if isinstance(payload, bytes):
            charset = encoding or "utf-8"
            try:
                parts.append(payload.decode(charset, errors="replace"))
            except LookupError:
                parts.append(payload.decode("utf-8", errors="replace"))
        else:
            parts.append(payload)
    return "".join(parts).strip()


def parse_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return decode_mime(value)
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone()
    return parsed.strftime("%Y-%m-%d %H:%M")


def domain_from_email(address: str) -> str:
    if "@" not in address:
        return ""
    return address.rsplit("@", 1)[1].lower().strip(" >")


def org_from_domain(domain: str) -> str:
    labels = [part for part in domain.lower().strip(".").split(".") if part]
    while len(labels) > 2 and labels[0] in COMMON_HOST_PREFIXES:
        labels.pop(0)

    for suffix in SAUDI_DOMAIN_SUFFIXES:
        suffix_labels = suffix.split(".")
        if labels[-len(suffix_labels) :] == suffix_labels and len(labels) > len(
            suffix_labels
        ):
            return labels[-len(suffix_labels) - 1].replace("-", " ").title()

    if len(labels) >= 2:
        return labels[-2].replace("-", " ").title()
    return domain.title()


def guess_org(sender_name: str, sender_domain: str, subject: str, body: str) -> str:
    clean_name = sender_name.strip().strip('"')
    clean_name = re.sub(
        r"\b(no[-_ ]?reply|noreply|careers?|recruiting|recruitment|hr|jobs?|talent|team)\b",
        "",
        clean_name,
        flags=re.IGNORECASE,
    )
    for generic_word in GENERIC_ARABIC_SENDER_WORDS:
        clean_name = clean_name.replace(generic_word, "")
    clean_name = SPACE_RE.sub(" ", clean_name).strip(" -_|")
    if clean_name and "@" not in clean_name and len(clean_name) > 2:
        return clean_name

    if sender_domain and sender_domain not in GENERIC_DOMAINS:
        return org_from_domain(sender_domain)

    patterns = [
        r"at\s+([A-Z][A-Za-z0-9& .'-]{2,60})",
        r"from\s+([A-Z][A-Za-z0-9& .'-]{2,60})",
        r"لدى\s+([\u0600-\u06FF A-Za-z0-9& .'-]{2,60})",
        r"في\s+([\u0600-\u06FF A-Za-z0-9& .'-]{2,60})",
    ]
    haystack = f"{subject}\n{body[:2000]}"
    for pattern in patterns:
        match = re.search(pattern, haystack)
        if match:
            return SPACE_RE.sub(" ", match.group(1)).strip(" .:-")

    return sender_domain or "unknown"


def text_from_message(message: Message) -> str:
    chunks: list[str] = []

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", "")).lower()
            if "attachment" in disposition:
                continue
            if content_type in {"text/plain", "text/html"}:
                chunks.append(decode_payload(part, strip_html=content_type == "text/html"))
    else:
        chunks.append(
            decode_payload(message, strip_html=message.get_content_type() == "text/html")
        )

    return normalize_text("\n".join(chunk for chunk in chunks if chunk))


def decode_payload(message: Message, strip_html: bool = False) -> str:
    payload = message.get_payload(decode=True)
    if payload is None:
        raw = message.get_payload()
        text = raw if isinstance(raw, str) else ""
    else:
        charset = message.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")

    if strip_html:
        text = html.unescape(TAG_RE.sub(" ", text))
    return text


def normalize_text(value: str) -> str:
    return SPACE_RE.sub(" ", html.unescape(value)).strip()


def clip_text(value: str, limit: int) -> str:
    value = normalize_text(value)
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 3)].rstrip() + "..."


def contains_term(lowered_text: str, term: str) -> bool:
    lowered_term = term.lower()
    if re.search(r"[a-z0-9]", lowered_term):
        pattern = rf"(?<![a-z0-9]){re.escape(lowered_term)}(?![a-z0-9])"
        return re.search(pattern, lowered_text) is not None
    return lowered_term in lowered_text


def find_terms(text: str, terms: Iterable[str]) -> list[str]:
    lowered = text.lower()
    return sorted({term for term in terms if contains_term(lowered, term)})


def sender_looks_recruiting(
    sender_name: str, sender_email: str, sender_domain: str
) -> bool:
    local_part = sender_email.split("@", 1)[0] if "@" in sender_email else sender_email
    text = f"{sender_name} {local_part} {sender_domain}"
    return bool(find_terms(text, RECRUITING_SENDER_TERMS))


def is_probable_application(
    searchable: str,
    sender_name: str,
    sender_email: str,
    sender_domain: str,
    status: str,
    matched_ats_terms: list[str],
) -> bool:
    direct_terms = find_terms(searchable, DIRECT_APPLICATION_TERMS)
    context_terms = find_terms(searchable, APPLICATION_CONTEXT_TERMS)
    role_terms = find_terms(searchable, ROLE_CONTEXT_TERMS)
    negative_terms = find_terms(searchable, NON_APPLICATION_TERMS)
    has_status_signal = status != "possible_application"
    recruiting_sender = sender_looks_recruiting(sender_name, sender_email, sender_domain)

    if negative_terms and not (
        direct_terms and has_status_signal and recruiting_sender
    ):
        return False
    if direct_terms:
        return True
    if role_terms and (context_terms or has_status_signal or recruiting_sender):
        return True
    if matched_ats_terms and (context_terms or recruiting_sender):
        return True
    if recruiting_sender and (context_terms or has_status_signal):
        return True
    return False


def infer_status(text: str) -> str:
    lowered = text.lower()
    matched_statuses: set[str] = set()
    for status, patterns in STATUS_PATTERNS:
        if any(contains_term(lowered, pattern) for pattern in patterns):
            matched_statuses.add(status)

    status_priority = [
        "ineligible",
        "rejected",
        "closed_or_full",
        "start_or_onboarding",
        "interview",
        "offer_or_accepted",
        "action_required",
        "under_review",
        "submitted_or_received",
    ]
    for status in status_priority:
        if status in matched_statuses:
            return status
    return "possible_application"


def infer_application_type(text: str) -> str:
    for application_type, terms in APPLICATION_TYPE_PATTERNS:
        if find_terms(text, terms):
            return application_type
    if find_terms(text, ATS_TERMS):
        return "career_portal"
    return "unknown_application"


def infer_confidence(
    text: str,
    status: str,
    matched_application_terms: list[str],
    matched_ats_terms: list[str],
    links: str,
) -> str:
    score = 0
    score += len(find_terms(text, HIGH_SIGNAL_TERMS)) * 3
    score += min(len(matched_application_terms), 5)
    score += min(len(matched_ats_terms), 3) * 2
    if status != "possible_application":
        score += 2
    if links:
        score += 1

    if score >= 8:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def infer_review_bucket(application_type: str, status: str, confidence: str) -> str:
    if (
        confidence == "high"
        and application_type != "unknown_application"
        and status != "possible_application"
    ):
        return "auto_classified"
    return "needs_review"


def message_to_record(message: Message, include_weak: bool = False) -> ApplicationEmail | None:
    subject = decode_mime(message.get("Subject"))
    sender_header = decode_mime(message.get("From"))
    parsed_sender = getaddresses([sender_header])
    sender_name, sender_email = parsed_sender[0] if parsed_sender else ("", "")
    sender_name = decode_mime(sender_name)
    sender_domain = domain_from_email(sender_email)
    body = text_from_message(message)
    searchable = f"{subject}\n{sender_header}\n{sender_domain}\n{body}"

    matched_application_terms = find_terms(searchable, APPLICATION_TERMS)
    matched_ats_terms = find_terms(searchable, ATS_TERMS)
    if not matched_application_terms and not matched_ats_terms:
        return None
    status = infer_status(searchable)
    if not include_weak and not is_probable_application(
        searchable,
        sender_name,
        sender_email,
        sender_domain,
        status,
        matched_ats_terms,
    ):
        return None

    links = " | ".join(URL_RE.findall(body)[:8])
    snippet_source = body or subject
    snippet = normalize_text(snippet_source[:500])
    organization = guess_org(sender_name, sender_domain, subject, body)
    matched_terms = ", ".join(sorted(set(matched_application_terms + matched_ats_terms)))
    application_type = infer_application_type(searchable)
    confidence = infer_confidence(
        searchable,
        status,
        matched_application_terms,
        matched_ats_terms,
        links,
    )

    return ApplicationEmail(
        date=parse_date(message.get("Date")),
        sender_name=sender_name,
        sender_email=sender_email,
        sender_domain=sender_domain,
        organization_guess=organization,
        subject=subject,
        application_type=application_type,
        status=status,
        confidence=confidence,
        review_bucket=infer_review_bucket(application_type, status, confidence),
        matched_terms=matched_terms,
        links=links,
        snippet=snippet,
    )


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_links(value: str) -> list[str]:
    return [link.strip() for link in value.split(" | ") if link.strip()]


def build_summary(records: list[ApplicationEmail]) -> list[dict[str, str]]:
    grouped: dict[str, list[ApplicationEmail]] = defaultdict(list)
    for record in records:
        grouped[record.organization_guess].append(record)

    summary_rows: list[dict[str, str]] = []
    for organization, items in grouped.items():
        status_counts = Counter(item.status for item in items)
        type_counts = Counter(item.application_type for item in items)
        review_counts = Counter(item.review_bucket for item in items)
        sorted_items = sorted(items, key=lambda item: item.date)
        domains = sorted({item.sender_domain for item in items if item.sender_domain})
        summary_rows.append(
            {
                "organization_guess": organization,
                "email_count": str(len(items)),
                "first_seen": sorted_items[0].date,
                "last_seen": sorted_items[-1].date,
                "statuses": "; ".join(
                    f"{status}:{count}" for status, count in status_counts.most_common()
                ),
                "application_types": "; ".join(
                    f"{kind}:{count}" for kind, count in type_counts.most_common()
                ),
                "review_buckets": "; ".join(
                    f"{bucket}:{count}" for bucket, count in review_counts.most_common()
                ),
                "domains": " | ".join(domains),
                "latest_subject": sorted_items[-1].subject,
            }
        )

    return sorted(summary_rows, key=lambda row: row["organization_guess"].lower())


def write_html_report(
    path: Path, records: list[ApplicationEmail], summary_rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    status_counts = Counter(record.status for record in records)

    grouped: dict[str, list[ApplicationEmail]] = defaultdict(list)
    for record in records:
        grouped[record.organization_guess].append(record)

    def esc(value: str) -> str:
        return html.escape(value or "", quote=True)

    status_items = "".join(
        f"<span class=\"pill\">{esc(status)}: {count}</span>"
        for status, count in status_counts.most_common()
    )
    empty_state = ""
    if not records:
        empty_state = """
        <section class="empty">
          <h2>No likely application emails found</h2>
          <p>Strict mode rejected weak keyword matches. If you expected results, rerun with <code>--include-weak</code> and manually review the noisy audit list.</p>
        </section>
        """

    summary_html = "\n".join(
        "<tr>"
        f"<td>{esc(row['organization_guess'])}</td>"
        f"<td>{esc(row['email_count'])}</td>"
        f"<td>{esc(row['first_seen'])}</td>"
        f"<td>{esc(row['last_seen'])}</td>"
        f"<td>{esc(row['statuses'])}</td>"
        f"<td>{esc(row['application_types'])}</td>"
        f"<td>{esc(row['review_buckets'])}</td>"
        f"<td>{esc(row['latest_subject'])}</td>"
        "</tr>"
        for row in summary_rows
    )

    detail_sections: list[str] = []
    for organization, items in sorted(grouped.items(), key=lambda item: item[0].lower()):
        rows: list[str] = []
        for record in sorted(items, key=lambda item: item.date):
            links = split_links(record.links)
            rendered_links = " ".join(
                f"<a href=\"{esc(link)}\">link {index}</a>"
                for index, link in enumerate(links, start=1)
            )
            rows.append(
                "<tr>"
                f"<td>{esc(record.date)}</td>"
                f"<td>{esc(record.application_type)}</td>"
                f"<td><span class=\"status\">{esc(record.status)}</span></td>"
                f"<td>{esc(record.confidence)}</td>"
                f"<td>{esc(record.review_bucket)}</td>"
                f"<td dir=\"auto\">{esc(record.subject)}</td>"
                f"<td dir=\"auto\">{esc(record.sender_name)}<br><small>{esc(record.sender_email)}</small></td>"
                f"<td dir=\"auto\">{rendered_links}</td>"
                f"<td dir=\"auto\">{esc(record.snippet)}</td>"
                "</tr>"
            )
        detail_sections.append(
            f"""
            <section>
              <h2 dir="auto">{esc(organization)}</h2>
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Confidence</th>
                    <th>Review</th>
                    <th>Subject</th>
                    <th>Sender</th>
                    <th>Links</th>
                    <th>Snippet</th>
                  </tr>
                </thead>
                <tbody>{''.join(rows)}</tbody>
              </table>
            </section>
            """
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Inbox Application Report</title>
  <style>
    body {{
      color: #111827;
      font-family: Arial, "Geeza Pro", sans-serif;
      line-height: 1.45;
      margin: 32px;
    }}
    h1 {{ font-size: 28px; margin: 0 0 4px; }}
    h2 {{ border-bottom: 1px solid #e5e7eb; font-size: 20px; margin-top: 32px; padding-bottom: 6px; }}
    .meta {{ color: #4b5563; margin: 0 0 20px; }}
    .empty {{ background: #f9fafb; border: 1px solid #e5e7eb; margin: 20px 0; padding: 14px 16px; }}
    .empty h2 {{ border: 0; margin: 0 0 6px; padding: 0; }}
    .empty p {{ margin: 0; }}
    .pills {{ margin: 14px 0 24px; }}
    .pill, .status {{
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      border-radius: 999px;
      display: inline-block;
      font-size: 12px;
      margin: 0 6px 6px 0;
      padding: 3px 8px;
      white-space: nowrap;
    }}
    table {{ border-collapse: collapse; margin: 12px 0 24px; table-layout: fixed; width: 100%; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; word-wrap: break-word; }}
    th {{ background: #f9fafb; font-size: 12px; text-transform: uppercase; }}
    small {{ color: #6b7280; }}
    a {{ color: #1d4ed8; }}
    @media print {{
      body {{ margin: 18mm; }}
      section {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <h1>Inbox Application Report</h1>
  <p class="meta">Generated {esc(generated_at)}. Found {len(records)} likely application emails across {len(summary_rows)} organizations.</p>
  <div class="pills">{status_items}</div>
  {empty_state}

  <h2>Organization Summary</h2>
  <table>
    <thead>
      <tr>
        <th>Organization</th>
        <th>Emails</th>
        <th>First Seen</th>
        <th>Last Seen</th>
        <th>Statuses</th>
        <th>Types</th>
        <th>Review</th>
        <th>Latest Subject</th>
      </tr>
    </thead>
    <tbody>{summary_html}</tbody>
  </table>

  {''.join(detail_sections)}
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")


def shape_pdf_text(value: str) -> str:
    text = normalize_text(str(value or ""))
    if not RTL_RE.search(text):
        return text

    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError:
        return text

    return get_display(arabic_reshaper.reshape(text))


def pdf_paragraph(value: str, style):
    from reportlab.platypus import Paragraph

    return Paragraph(html.escape(shape_pdf_text(value), quote=True), style)


def register_pdf_fonts() -> tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    regular_name = "Helvetica"
    bold_name = "Helvetica-Bold"

    for font_path in PDF_FONT_CANDIDATES:
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont("InboxReportRegular", font_path))
            regular_name = "InboxReportRegular"
            break

    for font_path in PDF_BOLD_FONT_CANDIDATES:
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont("InboxReportBold", font_path))
            bold_name = "InboxReportBold"
            break

    if regular_name != "Helvetica" and bold_name == "Helvetica-Bold":
        bold_name = regular_name

    return regular_name, bold_name


def write_pdf_report(
    path: Path, records: list[ApplicationEmail], summary_rows: list[dict[str, str]]
) -> bool:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    regular_font, bold_font = register_pdf_fonts()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName=bold_font,
            fontSize=22,
            leading=26,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=8,
            leading=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSmall",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#374151"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["BodyText"],
            fontName=bold_font,
            fontSize=7,
            leading=9,
            textColor=colors.white,
        )
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    flowables = [
        pdf_paragraph("Inbox Application Report", styles["ReportTitle"]),
        pdf_paragraph(
            f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
            f"Found {len(records)} likely application emails across {len(summary_rows)} organizations.",
            styles["ReportBody"],
        ),
        Spacer(1, 10),
    ]

    status_counts = Counter(record.status for record in records)
    status_line = " | ".join(
        f"{status}: {count}" for status, count in status_counts.most_common()
    )
    flowables.append(pdf_paragraph(status_line or "No application emails found.", styles["ReportBody"]))
    flowables.append(Spacer(1, 12))
    if not records:
        flowables.append(pdf_paragraph("No likely application emails found", styles["SectionTitle"]))
        flowables.append(
            pdf_paragraph(
                "Strict mode rejected weak keyword matches. If you expected results, "
                "rerun with --include-weak and manually review the noisy audit list.",
                styles["ReportBody"],
            )
        )
        doc.build(flowables)
        return True

    flowables.append(pdf_paragraph("Organization Summary", styles["SectionTitle"]))

    summary_table_data = [
        [
            pdf_paragraph("Organization", styles["TableHeader"]),
            pdf_paragraph("Emails", styles["TableHeader"]),
            pdf_paragraph("First Seen", styles["TableHeader"]),
            pdf_paragraph("Last Seen", styles["TableHeader"]),
            pdf_paragraph("Statuses", styles["TableHeader"]),
            pdf_paragraph("Types", styles["TableHeader"]),
            pdf_paragraph("Review", styles["TableHeader"]),
            pdf_paragraph("Latest Subject", styles["TableHeader"]),
        ]
    ]
    for row in summary_rows:
        summary_table_data.append(
            [
                pdf_paragraph(row["organization_guess"], styles["ReportBody"]),
                pdf_paragraph(row["email_count"], styles["ReportBody"]),
                pdf_paragraph(row["first_seen"], styles["ReportBody"]),
                pdf_paragraph(row["last_seen"], styles["ReportBody"]),
                pdf_paragraph(row["statuses"], styles["ReportBody"]),
                pdf_paragraph(row["application_types"], styles["ReportBody"]),
                pdf_paragraph(row["review_buckets"], styles["ReportBody"]),
                pdf_paragraph(clip_text(row["latest_subject"], 90), styles["ReportBody"]),
            ]
        )

    summary_table = Table(
        summary_table_data,
        colWidths=[
            1.05 * inch,
            0.4 * inch,
            0.65 * inch,
            0.65 * inch,
            0.95 * inch,
            0.75 * inch,
            0.75 * inch,
            1.35 * inch,
        ],
        repeatRows=1,
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flowables.append(summary_table)
    flowables.append(PageBreak())
    flowables.append(pdf_paragraph("Email Details", styles["SectionTitle"]))

    grouped: dict[str, list[ApplicationEmail]] = defaultdict(list)
    for record in records:
        grouped[record.organization_guess].append(record)

    for organization, items in sorted(grouped.items(), key=lambda item: item[0].lower()):
        flowables.append(pdf_paragraph(organization, styles["SectionTitle"]))
        for record in sorted(items, key=lambda item: item.date):
            links = split_links(record.links)
            detail_lines = [
                f"Date: {record.date}",
                f"Type: {record.application_type}",
                f"Status: {record.status}",
                f"Confidence: {record.confidence}",
                f"Review: {record.review_bucket}",
                f"Subject: {record.subject}",
                f"From: {record.sender_name} <{record.sender_email}>",
            ]
            if links:
                detail_lines.append(f"Links: {clip_text(' | '.join(links), 180)}")
            if record.snippet:
                detail_lines.append(f"Snippet: {clip_text(record.snippet, 320)}")

            detail_table = Table(
                [[pdf_paragraph(line, styles["ReportSmall"])] for line in detail_lines],
                colWidths=[6.55 * inch],
            )
            detail_table.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            flowables.append(detail_table)
            flowables.append(Spacer(1, 5))

    doc.build(flowables)
    return True


def iter_eml_messages(path: Path) -> Iterator[Message]:
    eml_paths = (
        [path]
        if path.is_file()
        else sorted(child for child in path.rglob("*") if child.suffix.lower() == ".eml")
    )
    parser = BytesParser(policy=default)
    for eml_path in eml_paths:
        with eml_path.open("rb") as handle:
            yield parser.parse(handle)


def iter_mbox_messages(path: Path) -> Iterator[Message]:
    mbox_path = path
    if path.is_dir():
        packaged_mbox = path / "mbox"
        if not packaged_mbox.exists():
            raise ValueError(
                f"directory does not look like an Apple Mail .mbox package or .eml export: {path}"
            )
        mbox_path = packaged_mbox
    box = mailbox.mbox(mbox_path)
    try:
        for message in box:
            yield message
    finally:
        box.close()


def is_inside_mbox_package(path: Path, root: Path) -> bool:
    for parent in path.parents:
        if parent == root:
            return False
        if parent.suffix.lower() == ".mbox":
            return True
    return False


def iter_directory_messages(path: Path) -> Iterator[Message]:
    mbox_packages = sorted(
        child
        for child in path.rglob("*")
        if child.is_dir() and child.suffix.lower() == ".mbox"
    )
    mbox_files = sorted(
        child
        for child in path.rglob("*")
        if child.is_file()
        and child.suffix.lower() == ".mbox"
        and not is_inside_mbox_package(child, path)
    )
    eml_files = sorted(
        child
        for child in path.rglob("*")
        if child.is_file()
        and child.suffix.lower() == ".eml"
        and not is_inside_mbox_package(child, path)
    )

    if not (mbox_packages or mbox_files or eml_files):
        raise ValueError(f"directory does not contain .mbox or .eml exports: {path}")

    for mbox_package in mbox_packages:
        yield from iter_mbox_messages(mbox_package)
    for mbox_file in mbox_files:
        yield from iter_mbox_messages(mbox_file)
    for eml_file in eml_files:
        yield from iter_eml_messages(eml_file)


def iter_input_messages(path: Path) -> Iterator[Message]:
    if path.is_dir():
        if path.suffix.lower() == ".mbox":
            yield from iter_mbox_messages(path)
            return
        yield from iter_directory_messages(path)
        return

    suffix = path.suffix.lower()
    if suffix == ".eml":
        yield from iter_eml_messages(path)
        return
    if suffix == ".pst":
        raise ValueError(
            "PST files are not parsed directly yet. Export or convert Outlook mail to "
            "an .eml folder, then run this tool on that folder."
        )
    if suffix == ".olm":
        raise ValueError(
            "OLM files are not parsed directly yet. Export or convert Outlook mail to "
            "an .eml folder, then run this tool on that folder."
        )

    yield from iter_mbox_messages(path)


def read_application_records(path: Path, include_weak: bool = False) -> list[ApplicationEmail]:
    records: list[ApplicationEmail] = []
    for message in iter_input_messages(path):
        record = message_to_record(message, include_weak=include_weak)
        if record:
            records.append(record)
    records.sort(key=lambda record: record.date)
    return records


def resolve_output_paths(args: argparse.Namespace) -> argparse.Namespace:
    output_dir = args.out.parent
    if args.summary_out is None:
        args.summary_out = output_dir / "applications_summary.csv"
    if args.html_out is None:
        args.html_out = output_dir / "applications_report.html"
    if args.pdf_out is None:
        args.pdf_out = output_dir / "applications_report.pdf"
    return args


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find likely job/coop application emails in an mbox or eml export.",
        epilog="mood: ابي اتوظظظظظظفففففف",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "input",
        type=Path,
        help="Path to exported .mbox file, .eml file, or folder of .eml files",
    )
    parser.add_argument(
        "--out",
        "--output",
        dest="out",
        type=Path,
        default=Path("applications.csv"),
        help="Detailed CSV output path",
    )
    parser.add_argument(
        "--summary-out",
        dest="summary_out",
        type=Path,
        default=None,
        help="Organization summary CSV output path; defaults next to --out",
    )
    parser.add_argument(
        "--html-out",
        "--html",
        dest="html_out",
        type=Path,
        default=None,
        help="Organized HTML report output path; defaults next to --out",
    )
    parser.add_argument(
        "--pdf-out",
        "--pdf",
        dest="pdf_out",
        type=Path,
        default=None,
        help="Organized PDF report output path; defaults next to --out",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation and only write CSV/HTML outputs",
    )
    parser.add_argument(
        "--include-weak",
        "--include-low-confidence",
        dest="include_weak",
        action="store_true",
        help="Audit mode: include weak keyword matches that strict mode filters out",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only write output files; suppress normal completion messages",
    )
    return resolve_output_paths(parser.parse_args(argv))


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2

    try:
        records = read_application_records(args.input, include_weak=args.include_weak)
    except ValueError as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2
    detail_rows = [record.__dict__ for record in records]
    fieldnames = list(ApplicationEmail.__dataclass_fields__.keys())
    summary_rows = build_summary(records)
    write_csv(args.out, detail_rows, fieldnames)
    write_csv(
        args.summary_out,
        summary_rows,
        [
            "organization_guess",
            "email_count",
            "first_seen",
            "last_seen",
            "statuses",
            "application_types",
            "review_buckets",
            "domains",
            "latest_subject",
        ],
    )
    write_html_report(args.html_out, records, summary_rows)

    wrote_pdf = False
    if not args.no_pdf:
        wrote_pdf = write_pdf_report(args.pdf_out, records, summary_rows)

    if not args.quiet:
        mode = "audit/include-weak" if args.include_weak else "strict"
        print(f"done: found {len(records)} likely application emails")
        print(f"mode: {mode}")
        if not records and not args.include_weak:
            print(
                "hint: no strong application confirmations found. "
                "Use --include-weak only when you want a noisy audit list."
            )
        print(f"details: {args.out}")
        print(f"summary: {args.summary_out}")
        print(f"html: {args.html_out}")
        if args.no_pdf:
            print("pdf: skipped")
        elif wrote_pdf:
            print(f"pdf: {args.pdf_out}")
        else:
            print("pdf: skipped because reportlab is not installed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
