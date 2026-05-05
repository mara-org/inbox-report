# How It Works

This is a local mailbox parser, not an email integration.

## Flow

1. The user exports email as an `.mbox` file, Apple Mail `.mbox` package, single `.eml`, or folder of `.eml` files.
2. The script reads MBOX with Python's standard `mailbox` module and EML with Python's email parser.
3. For each message, it decodes the subject, sender, date, text body, and links.
4. It checks the text against job, COOP, Tamheer, ATS, English, and Arabic terms.
5. Strict mode rejects weak-only matches such as social digests, store orders, newsletters, and generic order/status emails.
6. If the message still looks relevant, it creates one record.
7. It guesses:
   - organization
   - application type
   - status
   - rough deadline
   - next action
   - confidence
   - review bucket
8. It writes:
   - detailed CSV
   - organization summary CSV
   - student action summary CSV
   - HTML report
   - PDF report when optional PDF dependencies are installed

## Application Type

Application type answers: "What kind of opportunity does this email look like?"

Current values:

- `coop`: COOP / Cooperative Training / التدريب التعاوني
- `tamheer`: Tamheer / Hadaf / Taqat / on-the-job training
- `internship`: internship or summer training
- `graduate_program`: graduate program or fresh graduate track
- `job`: direct job application
- `training`: generic training opportunity
- `career_portal`: ATS or careers platform signal without enough type detail
- `unknown_application`: relevant-looking application email, but type is unclear

## Status Guessing

The status is rule-based. It is not pretending to be perfect.

Examples:

- `submitted_or_received`: application received / تم استلام طلبك
- `under_review`: under review / قيد المراجعة
- `action_required`: complete profile, upload document, assessment, login
- `interview`: interview invitation / دعوة للمقابلة
- `offer_or_accepted`: selected, accepted, offer / تم قبولك
- `start_or_onboarding`: start date, onboarding, مباشرة
- `ineligible`: not eligible / لم تستوف شروط الأهلية
- `closed_or_full`: vacancies filled / اكتمل العدد
- `rejected`: unfortunately / نعتذر / لم يتم اختيارك

## Confidence

Confidence is a simple signal:

- `high`: strong application language, Saudi COOP/Tamheer terms, ATS terms, known statuses, or links.
- `medium`: enough signs to review.
- `low`: weak match. Keep it in the report, but do not trust it blindly.

## Review Bucket

`review_bucket` is the accuracy guardrail.

- `auto_classified`: high confidence, clear application type, and clear status.
- `needs_review`: anything uncertain.

Do not claim 90-100% accuracy for every row. The correct claim is narrower: the tool is designed so high-confidence `auto_classified` rows should be the clean set, while `needs_review` rows are intentionally not treated as final.

## Student Action Summary

`student_summary.csv` is a lighter view for students who want to know what to do next. It sorts rows by priority:

- action required
- interview
- offer or accepted
- onboarding
- waiting
- closed
- needs review

The `next_step` field is rule-based. It can point out common actions such as completing an assessment, uploading a document, signing in to a portal, preparing for an interview, or tracking an application.

The `deadline` field is also rule-based. It looks for nearby phrases such as `deadline`, `due`, `by`, `before`, `no later than`, `الموعد النهائي`, `آخر موعد`, and `قبل`.

Treat both fields as reminders to review the original email, not as a replacement for reading the source message.

Default strict mode favors precision over recall. If strict mode returns no rows but you expected applications, run audit mode:

```bash
inbox-report /path/to/Mail.mbox --include-weak
```

Audit mode includes weak keyword matches that strict mode filters out. It is useful for debugging exports, but it is intentionally noisy and should not be used as the final PDF without manual review.

To prove a 90%+ number, build a labeled sample of real or synthetic emails, compare tool output against human labels, and report precision/recall separately for `auto_classified` and `needs_review`.

## Why Not OAuth?

OAuth would make onboarding smoother, but it changes the security model:

- users must grant mailbox access
- the project needs app verification and scopes
- mistakes can touch private inbox data
- hosting becomes a real data-protection responsibility

For students, the safer MVP is export-first and local-first.

## Why MBOX?

MBOX and EML are not glamorous, but they are useful:

- Gmail Takeout exports Mail archives this way.
- Apple Mail can export mailboxes this way.
- Outlook/Proton/Thunderbird workflows can produce EML files.
- It is readable without account credentials.
- Python can parse it with the standard library.

PST and OLM should be added as separate import adapters rather than replacing MBOX/EML.
