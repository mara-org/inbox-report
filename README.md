# Inbox Report

Turn local mailbox exports into structured application reports.

Inbox Report is a local CLI for students and early-career applicants who need to review a large mailbox of job, COOP, internship, Tamheer, and training applications without giving a tool live inbox access.

It reads `.mbox` and `.eml` exports, detects likely application-related messages, groups them by organization, infers rough status, and writes CSV, HTML, and PDF reports.

No inbox login.
No email password.
No cloud upload.
No external API.
No LLM.

Just a local parser and deterministic classifier for application review.

## Features

- Reads Gmail/Google Takeout-style `.mbox` files, Takeout `Mail/` folders, Apple Mail `.mbox` packages, and Outlook-friendly `.eml` folders.
- Detects likely job, COOP/cooperative training, Tamheer, internship, trainee, and application emails.
- Supports English and Arabic matching terms.
- Handles Saudi phrases like `التدريب التعاوني`, `برنامج التدريب التعاوني`, `التدريب على رأس العمل`, and `تمهير`.
- Groups emails by guessed organization.
- Classifies application type as `coop`, `tamheer`, `internship`, `graduate_program`, `job`, `training`, `career_portal`, or `unknown_application`.
- Infers rough status: `submitted_or_received`, `under_review`, `action_required`, `interview`, `offer_or_accepted`, `start_or_onboarding`, `ineligible`, `closed_or_full`, `rejected`, or `possible_application`.
- Adds `confidence` and `review_bucket`; only high-confidence rows with clear type and status are `auto_classified`.
- Extracts links, sender details, subjects, snippets, and dates.
- Writes editable CSV files plus organized HTML/PDF reports.

## Fast Path

```bash
git clone https://github.com/mara-org/inbox-report.git
cd inbox-report
make demo
```

That creates a fake mailbox and writes demo outputs under `.demo/`.

If you are using a real inbox, read the [Export Guide](docs/export-guide.md) first.

Useful commands:

```bash
make help
make check
make test
make demo
make report INPUT=/path/to/Mail.mbox
make audit INPUT=/path/to/Mail.mbox
make path-smoke
make agent-check
```

## Install

Python 3.9+ is supported.

```bash
git clone https://github.com/mara-org/inbox-report.git
cd inbox-report
python3 -m pip install -r requirements.txt
```

Local package install:

```bash
python3 -m pip install -e ".[pdf]"
inbox-report --version
```

Install from PyPI:

```bash
python3 -m pip install "inbox-report[pdf]"
inbox-report --version
```

The core CSV/HTML flow uses Python's standard library. PDF output uses `reportlab`; Arabic shaping in the PDF uses `arabic-reshaper` and `python-bidi`.

## Usage

1. Export Gmail from [Google Takeout](https://takeout.google.com/) and include Mail only, or export an `.eml` folder from a desktop mail client.
2. Wait for the export email. Gmail Takeout can take minutes, hours, or longer for large mailboxes.
3. Download and unzip the Takeout archive.
4. Find the `Mail` folder or the `.mbox` file inside it.
5. Run:

Gmail / MBOX:

```bash
inbox-report /path/to/Takeout/Mail
inbox-report /path/to/Mail.mbox
```

Same thing through Make:

```bash
make report INPUT=/path/to/Mail.mbox
```

Strict mode is the default. It is intentionally conservative and filters out social digests, store orders, newsletters, and weak keyword matches. If you expected results and got an empty report, use audit mode to inspect noisy candidates:

```bash
inbox-report /path/to/Mail.mbox --include-weak
make audit INPUT=/path/to/Mail.mbox
```

Audit mode is for review, not final proof. Treat `needs_review` rows as "look at this manually", not as confirmed applications.

EML folder:

```bash
inbox-report /path/to/exported-emails/
```

Direct script usage also works:

```bash
python3 inbox_application_reporter.py /path/to/Mail.mbox
```

## Gmail Export Quick Steps

1. Open [Google Takeout](https://takeout.google.com/).
2. Click **Deselect all**.
3. Enable **Mail** only.
4. Click **Next step**.
5. Choose `.zip` and **Send download link via email**.
6. Click **Create export**.
7. Wait for Google's email.
8. Download, unzip, and find the `.mbox` file inside the Mail folder.

Large exports are normal. If it does not arrive immediately, wait; it does not mean the export failed.

Custom output paths:

```bash
inbox-report /path/to/Mail.mbox \
  --out details.csv \
  --summary-out companies.csv \
  --html-out report.html \
  --pdf-out report.pdf
```

Short aliases are also supported for scripts and agents:

```bash
inbox-report /path/to/Takeout/Mail --output details.csv --html report.html --pdf report.pdf
```

Skip PDF generation:

```bash
inbox-report /path/to/Mail.mbox --no-pdf
```

Version:

```bash
inbox-report --version
```

## Technical Overview

Inbox Report is intentionally deterministic. It does not classify messages with a remote model or send mailbox text to a service.

The pipeline is:

1. Parse local mailbox exports with Python's standard email and mailbox libraries.
2. Decode MIME headers and message bodies, including plain text and HTML email bodies.
3. Normalize whitespace and extract sender, domain, subject, date, snippets, and links.
4. Match application signals across English and Arabic term sets.
5. Apply negative filters for common false positives such as store orders, newsletters, social digests, policy emails, discounts, shipping, and invoices.
6. Infer application type, status, confidence, and review bucket.
7. Write machine-readable CSV outputs and human-readable HTML/PDF reports.

The classifier favors precision in strict mode. Direct application confirmations, ATS domains, recruiting senders, role context, and status phrases increase confidence. Weak keyword matches are excluded by default and only appear when `--include-weak` is used.

Need the export steps? Start here:

- [Export Guide](docs/export-guide.md)
- [How It Works](docs/how-it-works.md)
- [PyPI Publishing](docs/pypi-publishing.md)
- [Roadmap](docs/roadmap.md)
- [LinkedIn Post Draft](docs/linkedin-post.md)

## PyPI

The PyPI package name is `inbox-report`. Publishing is configured through GitHub Actions trusted publishing, so no PyPI token is needed in the repo.

On PyPI's **Trusted Publisher Management** page, add a pending GitHub publisher with:

- PyPI Project Name: `inbox-report`
- Owner: `mara-org`
- Repository name: `inbox-report`
- Workflow name: `publish.yml`
- Environment name: `pypi`

Then publish by pushing a version tag like `v1.0.1`, creating a GitHub Release, or manually running the `publish` workflow from GitHub Actions.

## Outputs

- `applications.csv`: every matched email with sender, date, subject, guessed organization, application type, status, confidence, review bucket, links, matched terms, and snippet.
- `applications_summary.csv`: one row per guessed organization with counts, first/last seen dates, status counts, type counts, review counts, domains, and latest subject.
- `applications_report.html`: browser-friendly report grouped by organization.
- `applications_report.pdf`: PDF report when optional PDF dependencies are installed.

## Security And Privacy Model

This tool reads a local export file. It does not send email, log in to Gmail, modify messages, upload data, or call an external API.

Mailbox exports can contain sensitive personal data. Treat `.mbox`, CSV, HTML, and PDF outputs as private unless you intentionally redact and share them.

## Accuracy Guardrails

The classifier is rule-based and tested with synthetic fixtures for Gmail-style confirmations, LinkedIn, Workday, Greenhouse, Lever, SmartRecruiters, Saudi COOP, Tamheer, interviews, offers, rejections, onboarding, store orders, newsletters, social digests, and marketing emails.

Strict mode favors precision. Audit mode exists for recall and manual review. Do not present `needs_review` rows as confirmed applications.

## Contributing

PRs are welcome. The best PRs make detection better without making the privacy story worse.

Good areas:

- better status detection
- more ATS domains
- safer organization guessing
- tests with synthetic fixtures
- packaging

Please do not include real mailbox exports, personal emails, screenshots of inboxes, or private identifiers in issues or PRs.

## Maintainers

Maintained by [Mara](https://github.com/mara-org).
Created by [@gqnxx](https://github.com/gqnxx).

Regards,
The CTO.
