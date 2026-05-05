# Contributing

Thanks for improving Inbox Application Reporter.

## Good PRs

- Keep changes small and focused.
- Use synthetic `.mbox` fixtures only.
- Do not commit real emails, resumes, phone numbers, access tokens, or generated reports from real inboxes.
- Add or update tests when changing matching, grouping, parsing, or output behavior.
- Explain privacy implications when adding integrations.

## Local Checks

```bash
make check
```

If you add test fixtures, prefer tiny artificial messages that exercise one behavior at a time.
