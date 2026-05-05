# Quickstart For Students

Inbox Report turns a local email export into a private application tracker. It does not ask for your email password and it does not connect to Gmail, Outlook, or any cloud service.

## 1. Check Python

Python 3.9 or newer is required.

macOS or Linux:

```bash
python3 --version
```

Windows PowerShell:

```powershell
py --version
```

## 2. Get The Project

macOS or Linux:

```bash
git clone https://github.com/mara-org/inbox-report.git
cd inbox-report
```

Windows PowerShell:

```powershell
git clone https://github.com/mara-org/inbox-report.git
cd inbox-report
```

## 3. Try The Demo First

The demo uses fake emails only.

macOS or Linux:

```bash
make demo
open .demo/applications_report.html
```

Windows PowerShell:

```powershell
py tests/make_sample_mbox.py .demo/sample.mbox
py inbox_application_reporter.py .demo/sample.mbox --no-pdf
```

Open `applications_report.html` in your browser.

## 4. Export Your Email

For Gmail, use Google Takeout:

1. Go to https://takeout.google.com/.
2. Click **Deselect all**.
3. Select **Mail** only.
4. Click **Next step**.
5. Choose `.zip`.
6. Choose **Send download link via email**.
7. Click **Create export**.
8. Wait for Google's email, then download and unzip the archive.
9. Find the `Mail` folder or a file ending in `.mbox`.

More options are in [docs/export-guide.md](docs/export-guide.md).

## 5. Run On Your Export

macOS or Linux:

```bash
python3 inbox_application_reporter.py /path/to/Takeout/Mail --friendly-labels --no-pdf
```

Windows PowerShell:

```powershell
py inbox_application_reporter.py "C:\path\to\Takeout\Mail" --friendly-labels --no-pdf
```

The most useful file for students is:

```text
student_summary.csv
```

It sorts rows by what needs attention first.

## 6. If The Report Is Empty

Strict mode avoids noisy matches. If you expected applications and got zero rows, run audit mode:

```bash
python3 inbox_application_reporter.py /path/to/Mail.mbox --include-weak --friendly-labels --no-pdf
```

Audit mode can include false positives. Manually review rows marked `Needs review`.

## 7. Share Safely

Mailbox reports can contain private emails, links, application IDs, and message snippets. Use redacted mode before sharing:

```bash
python3 inbox_application_reporter.py /path/to/Mail.mbox --redact --friendly-labels --no-pdf
```
