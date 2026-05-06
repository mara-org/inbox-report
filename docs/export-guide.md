# Export Guide

Inbox Report reads local `.mbox` and `.eml` files.

## Gmail

Use Google Takeout:

1. Open https://takeout.google.com/.
2. Click **Deselect all**.
3. Select **Mail** only.
4. Choose `.zip`.
5. Create the export.
6. Download and unzip it.
7. Use the `Takeout/Mail` folder or the `.mbox` file inside it.

Run:

```bash
python3 inbox_application_reporter.py report /path/to/Takeout/Mail --open
```

## Apple Mail

1. Open Mail on Mac.
2. Select a mailbox.
3. Choose **Mailbox -> Export Mailbox**.
4. Run Inbox Report on the exported `.mbox` folder.

## Outlook

Direct `.pst` and `.olm` parsing is not supported yet.

Use one of these instead:

- export or save messages as `.eml`
- sync the account into Apple Mail and export `.mbox`
- convert PST/OLM to EML or MBOX first

## Privacy

Do not upload real mailbox exports to random websites. `.mbox`, CSV, HTML, and PDF files can contain names, emails, links, phone numbers, and application IDs.

Use redacted mode before sharing:

```bash
python3 inbox_application_reporter.py redact /path/to/Mail.mbox --open
```
