# Agent Handoff

Give this file to a coding agent such as Codex, Claude Code, Cursor, or another local terminal agent when you want it to run Inbox Report for you.

The agent still needs a local mailbox export path. It must not ask for an email password, OAuth login, Gmail access, or a cloud upload.

## Copy-Paste Prompt

```text
You are helping me run Inbox Report on my local machine.

Goal:
- Generate a private application report from my local mailbox export.
- Do not ask for my email password.
- Do not connect to Gmail, Outlook, or any live inbox.
- Do not upload my mailbox or report files anywhere.
- Do not commit or share real mailbox exports or generated reports.

Repository:
https://github.com/mara-org/inbox-report

Workflow:
1. Clone the repo if it is not already available.
2. Run the demo first with `make demo` if `make` exists. If not, run:
   `python3 tests/make_sample_mbox.py .demo/sample.mbox`
   `python3 inbox_application_reporter.py .demo/sample.mbox --no-pdf`
3. Confirm that the demo produced:
   - `.demo/student_summary.csv`
   - `.demo/applications.csv`
   - `.demo/applications_summary.csv`
   - `.demo/applications_report.html`
4. Ask me for the local path to my real export. It may be:
   - a Google Takeout `Mail` folder
   - a `.mbox` file
   - a folder of `.eml` files
5. When I give the path, run strict mode first:
   `python3 inbox_application_reporter.py "<EXPORT_PATH>" --friendly-labels --no-pdf`
6. Tell me where these files were written:
   - `student_summary.csv`
   - `applications.csv`
   - `applications_summary.csv`
   - `applications_report.html`
7. If strict mode finds zero rows and I expected applications, ask before running audit mode:
   `python3 inbox_application_reporter.py "<EXPORT_PATH>" --include-weak --friendly-labels --no-pdf`
8. If I want to share results, run redacted mode:
   `python3 inbox_application_reporter.py "<EXPORT_PATH>" --redact --friendly-labels --no-pdf`
9. Summarize the report in plain language:
   - items needing action
   - interviews
   - offers or onboarding
   - applications under review
   - rejected/closed/ineligible items
   - rows marked Needs review

Safety rules:
- Never print long private snippets from real emails into chat.
- Never paste private links, application IDs, phone numbers, or email addresses unless I explicitly ask.
- Prefer summarizing counts and next steps from `student_summary.csv`.
- Remind me that `needs_review` rows are not confirmed applications.
- If the export path does not exist, explain how to find the Takeout `Mail` folder or `.mbox` file.
```

## One-Line Version

```text
Clone https://github.com/mara-org/inbox-report, run `make demo`, ask me for my local Gmail Takeout Mail folder or `.mbox` path, run `python3 inbox_application_reporter.py "<EXPORT_PATH>" --friendly-labels --no-pdf`, then summarize `student_summary.csv` without exposing private email details.
```

## Expected Agent Output

The agent should end with something like:

```text
Report created.

Most useful file:
- student_summary.csv

Other files:
- applications.csv
- applications_summary.csv
- applications_report.html

Summary:
- Action required: 2
- Interviews: 1
- Under review: 8
- Needs review: 3

Open applications_report.html in your browser for the full local report.
```
