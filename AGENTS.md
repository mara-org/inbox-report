# Agent Notes

This repo is intentionally boring: one Python script, synthetic tests, and local files only.

## Safe Commands

```bash
make check
make test
make demo
make report INPUT=/path/to/export
make audit INPUT=/path/to/export
make path-smoke
make package
make agent-check
```

Use `make demo` when you need sample outputs. It creates a fake mailbox under `.demo/` and does not touch real user email.
Use `make report INPUT=...` only with a local export path the user explicitly provided.
Use `make audit INPUT=...` only when you need a noisy weak-match review pass.

## Privacy Rules

- Never commit real `.mbox` exports.
- Never commit generated reports from a real inbox.
- Never ask for an email password.
- Do not add live Gmail/OAuth sending behavior without a separate design and explicit consent.

## Project Shape

- `inbox_application_reporter.py`: CLI and report generation.
- `pyproject.toml`: package metadata and `inbox-report` console command.
- `tests/test_inbox_application_reporter.py`: unit tests with synthetic messages.
- `tests/make_sample_mbox.py`: fake mailbox generator used by `make demo`.

## Expected Checks

Before pushing:

```bash
make agent-check
```

If optional PDF dependencies are missing, CSV and HTML should still work. The demo is allowed to skip PDF only when `reportlab` is unavailable.
