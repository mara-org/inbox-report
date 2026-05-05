# Export Guide

The tool reads `.mbox` and `.eml` exports today. That is intentional: both formats are local, credential-free, and common enough to support without turning this into a live inbox integration.

## Best Format

| Source | Best path today | Works directly? | Notes |
| --- | --- | --- | --- |
| Gmail | Google Takeout -> `Mail/` folder or `.mbox` file | Yes | Recommended path. |
| Google Workspace Gmail | Google Takeout, if admin policy allows it | Yes | Some school/company accounts block Takeout. |
| Apple Mail on Mac | Mailbox -> Export Mailbox -> `.mbox` package | Yes | Good fallback for any account already synced into Apple Mail. |
| Outlook / Hotmail | Save/export messages as `.eml`, or convert PST to EML/MBOX | EML yes, PST no | Direct PST parsing is not supported yet. |
| Proton Mail | Proton export / Bridge / Thunderbird -> MBOX or EML | Yes | MBOX or EML both work. |
| Yahoo Mail | Sync into Apple Mail or Thunderbird, then export MBOX | Depends | Yahoo says it does not provide a direct export feature. |

## Gmail Export

Use this when the inbox is Gmail or a university account hosted on Google.

1. Open [Google Takeout](https://takeout.google.com/).
2. Click **Deselect all**.
3. Turn on **Mail** only.
4. If you want a smaller export, use the Mail options to choose only selected labels. If unsure, keep all Mail.
5. Click **Next step**.
6. Delivery method: **Send download link via email**.
7. File type: `.zip`.
8. Archive size: use the largest size available if the mailbox is huge.
9. Click **Create export**.
10. Wait for Google's email. This can take minutes, hours, or longer for large mailboxes. That delay is normal.
11. Download the archive and unzip it.
12. Find the `Mail` folder or the `.mbox` file inside it.
13. Run:

```bash
inbox-report /path/to/Takeout/Mail
inbox-report /path/to/Mail.mbox
```

Google's own help confirms Takeout can export data for products including Email and create a downloadable archive. It also notes the archive can take from minutes to days and may be split into multiple files.

## Apple Mail Export

Use this when the account is already synced into the Mail app on a Mac.

1. Open **Mail**.
2. Select the mailbox you want to export. For example: Inbox, All Mail, or a folder.
3. Choose **Mailbox -> Export Mailbox**.
4. Choose a destination folder.
5. Mail creates an `.mbox` package.
6. Run the tool on the exported `.mbox` path. Apple Mail often creates a folder ending in `.mbox`; that is supported.

Apple's own Mail guide says Mail can export mailboxes in MBOX format.

## Outlook / Hotmail

Outlook often exports to `.pst`, and PST is not parsed directly yet. The tool does support `.eml` files and folders, which are a better bridge format for now.

Current options:

- Save or export Outlook messages as `.eml` files when your Outlook client supports it.
- If you can sync the Outlook account into Apple Mail, export from Apple Mail as MBOX.
- If you know your way around Thunderbird, sync the account there and export an MBOX or EML folder.
- If you only have a `.pst`, convert it to EML/MBOX first, then run the tool on the converted folder/file.

Microsoft's support docs say Outlook.com mailbox export uses `.pst` on Windows or `.olm` on legacy Outlook for Mac.

## Proton Mail

Proton documents MBOX and EML export/import paths. This tool can read either MBOX or a folder of EML files.

## Yahoo Mail

Yahoo's help says Yahoo Mail does not have a direct export feature. The practical route is to connect Yahoo Mail to a desktop mail client, sync the messages, and export from that client.

## Privacy

Do not upload real mailbox exports to random websites. `.mbox`, CSV, HTML, and PDF files can contain private names, emails, phone numbers, application links, and attachments text.

The safest path is:

```bash
python3 inbox_application_reporter.py /path/to/Mail.mbox
```

Or:

```bash
python3 inbox_application_reporter.py /path/to/eml-folder/
```

Run it locally, review the output, then delete the raw export when you no longer need it.
