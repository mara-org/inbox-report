# Quickstart For Students

Inbox Report makes a private application tracker from a local email export. It does not ask for an email password or connect to your inbox.

## 1. Try The Demo

```bash
git clone https://github.com/mara-org/inbox-report.git
cd inbox-report
python3 inbox_application_reporter.py demo --open
```

## 2. Export Your Email

For Gmail:

1. Open https://takeout.google.com/.
2. Click **Deselect all**.
3. Select **Mail** only.
4. Choose `.zip`.
5. Create the export, download it, and unzip it.
6. Find `Takeout/Mail` or a `.mbox` file inside it.

More options: [docs/export-guide.md](docs/export-guide.md).

## 3. Run The Report

Easy mode:

```bash
python3 inbox_application_reporter.py wizard
```

Direct mode:

```bash
python3 inbox_application_reporter.py report /path/to/Takeout/Mail --open
```

If nothing shows up but you expected applications:

```bash
python3 inbox_application_reporter.py audit /path/to/Mail.mbox --open
```

Before sharing:

```bash
python3 inbox_application_reporter.py redact /path/to/Mail.mbox --open
```

## 4. Read This First

Open `student_summary.csv`. It is sorted by what needs attention first.

Rows marked `Needs review` are not confirmed applications. Check the original email before trusting them.
