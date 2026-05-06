# How It Works

Inbox Report is a local parser.

It does not log in to email, upload files, or call an AI model.

## Pipeline

1. Read `.mbox` or `.eml` messages.
2. Decode subject, sender, date, body, and links.
3. Match English and Arabic application terms.
4. Ignore common false positives like orders, newsletters, and social digests.
5. Guess organization, application type, status, confidence, deadline, and next action.
6. Write CSV, HTML, and optional PDF reports.

## Important Fields

- `student_summary.csv`: the first file most students should open.
- `status`: rough state such as action required, interview, under review, or rejected.
- `next_action`: simple guidance like complete an assessment or prepare for an interview.
- `deadline`: rough extracted due date when the email includes one.
- `review_bucket`: `auto_classified` or `needs_review`.

## Accuracy

Strict mode favors fewer false positives.

Audit mode finds more possible matches, but it is noisy:

```bash
python3 inbox_application_reporter.py audit /path/to/Mail.mbox --open
```

Treat `needs_review` rows as “check manually”, not as confirmed applications.
