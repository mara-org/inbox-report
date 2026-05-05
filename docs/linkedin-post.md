# LinkedIn Post Draft

I built a small open-source tool for Saudi students applying to COOP / التدريب التعاوني programs.

Problem:

By the end of the application season, your inbox becomes a mess:

- company portals
- ATS emails
- university training requirements
- Tamheer / Hadaf updates
- interview links
- rejection emails
- "complete your profile" emails

So I made **Inbox Application Reporter**.

It reads a local `.mbox` email export and turns it into:

- CSV with every likely application email
- company summary CSV
- HTML report
- PDF report

It is local-first:

- no Gmail password
- no inbox login
- no cloud upload
- no sending emails

It supports Saudi-relevant terms like:

- `التدريب التعاوني`
- `برنامج التدريب التعاوني`
- `التدريب على رأس العمل`
- `تمهير`
- COOP / Cooperative Training

Repo:

https://github.com/mara-org/inbox-report

If you are a student applying to COOP, clone it and run:

```bash
make demo
```

Then export your Gmail from Google Takeout and run:

```bash
python3 inbox_application_reporter.py /path/to/Mail.mbox
```

After the PyPI release:

```bash
python3 -m pip install "inbox-report[pdf]"
inbox-report /path/to/Mail.mbox
```

Still early, but useful. PRs are welcome, especially for better Saudi COOP/Tamheer email patterns and Outlook/PST support.

#OpenSource #SaudiTech #COOP #التدريب_التعاوني #Python #Students
