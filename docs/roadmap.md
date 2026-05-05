# Roadmap

This is what would make the tool stronger without turning it into a risky mailbox app.

## High Impact

- Add direct PST support for Outlook users.
- Improve Outlook docs with client-specific EML export screenshots.
- Add a `--since` / `--until` filter after parsing dates.
- Add `--terms-file` so universities can ship their own Arabic/English term lists.
- Add better organization normalization for Saudi companies and government entities.
- Add duplicate/thread detection so repeated status updates group better.

## Quality

- More synthetic fixtures for Saudi COOP, Tamheer, STC, SABIC, HRDF/Hadaf, and government-style emails.
- Golden CSV snapshots for output regression tests.
- Better Arabic PDF rendering checks.
- A small sample output screenshot in the README.

## Packaging

- Publish `inbox-report` to PyPI from a local release shell.
- Support `pipx install "inbox-report[pdf]"`.
- Keep the console command:

```bash
inbox-report /path/to/Mail.mbox
```

## What Not To Do Yet

- Do not add Gmail OAuth until there is a clear privacy/security design.
- Do not host a public upload site for real inbox exports without explicit data handling, deletion, logging, and legal policy.
- Do not send emails or follow-ups from this tool.
