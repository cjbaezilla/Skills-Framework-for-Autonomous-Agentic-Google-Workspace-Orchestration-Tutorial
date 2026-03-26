---
name: send-email
description: Sends an email using Gmail through the Google Gmail API with simple CLI
license: MIT
compatibility: opencode
metadata:
  category: google-workspace
  audience: developers, productivity-users
  script: send_email.py
---

## What I do

I send emails via Gmail using the Google Gmail API. My capabilities include:

- Simple argument-based interface (recipient, subject, body, optional CC)
- Alternative body-file input for multi-line content with proper formatting
 - Configurable sender name via `google_operations.py`
 - **Automatic HTML signature support**: HTML signature is always appended to all emails
 - Cached authentication with automatic token refresh
- Clean error reporting and exit codes
- Integration with Google's OAuth 2.0 flow

## When to use me

Use me when you need to:

- Send automated notifications from scripts or CI/CD pipelines
- Dispatch alerts or monitoring messages
- Send reports or summaries via email
- Integrate email functionality into automation workflows
- Quickly send emails without manual Gmail interface

## How to invoke me

```
python scripts/google/send_email.py --to "recipient@example.com" --subject "Hello" --body "Message body" [--no-signature]
```

## Parameters

**Required:**

- `--to`: Recipient email address (string)
- `--subject`: Email subject line (string)

**Optional:**

- `--cc`: CC recipient email address(es), comma-separated (string) - e.g., "cc1@example.com,cc2@example.com"

**Body (exactly one required):**

- `--body`: Email body content (string) - Accepts multi-line content with actual line breaks. Do NOT use `\n` or `\r` escape sequences. Text is automatically converted to HTML: blank lines create `<p>` paragraphs, single newlines become `<br />` tags. **Sent as HTML only**.
- `--body-file`: Path to a text file containing the email body - Use for multi-line content, preserving line breaks and formatting. Text is automatically converted to HTML: blank lines create `<p>` paragraphs, single newlines become `<br />` tags. **Sent as HTML only**.

You must provide either `--body` OR `--body-file`, but not both.

**HTML-ONLY POLICY**: The send-email skill sends emails **strictly in HTML format with NO plain text alternative**. The body content (whether from `--body` or `--body-file`) is automatically converted to HTML: blank lines become `<p>` paragraphs, single newlines become `<br />` tags, and special characters are escaped. Messages are single-part MIMEText with subtype 'html' only. **No `\n` or `\r` characters appear in the final HTML output**.

## Return values

On success:
- Exit code `0`
- Output: `Email sent successfully! ID: <message_id>`

On failure:
- Exit code `1`
- Error message printed to stderr

## Example usage

```bash
# Basic notification
python scripts/google/send_email.py \
  --to "team@example.com" \
  --subject "Build Complete" \
  --body "The latest build finished successfully. Artifacts: https://ci.example.com/build/123"

# Alert message with CC
python scripts/google/send_email.py \
  --to "admin@example.com" \
  --cc "manager@example.com,ops-team@example.com" \
  --subject "⚠️ Server Alert" \
  --body "CPU usage exceeded 90% on prod-server-01"

# Email with multi-line content (preserves formatting)
python scripts/google/send_email.py \
  --to "carlos.baeza@gmail.com" \
  --subject "Hackathon Coordination: Important Updates" \
  --body-file "email_body.txt"

# Send with signature (automatic)
python scripts/google/send_email.py \
  --to "carlos.baeza@gmail.com" \
  --subject "Weekly Report" \
  --body "See attached for this week's progress."

# Integration in Python scripts
import subprocess
result = subprocess.run([
    'python', 'scripts/google/send_email.py',
    '--to', 'devops@example.com',
    '--subject', 'Deployment Started',
    '--body', 'Deploying version 2.4.1 to production...'
], capture_output=True, text=True)
```

## Notes

- Requires Google OAuth credentials in `credentials/`
   - `google_credentials.json` (OAuth client secrets)
   - `google_token.json` (auto-generated on first run)
- First execution opens browser for authorization
- HTML signature support: configure `SIGNATURE_HTML_FILE` in `libs/google_operations.py`
- **STRICT HTML-ONLY**: All emails are sent **exclusively in HTML format** with absolutely no plain text alternative. The implementation uses single-part `MIMEText('html')` messages only.
- **Paragraph Formatting**: Input text is converted to HTML with proper paragraph structure:
  - Blank lines (double newlines) create separate `<p>` paragraphs
  - Single newlines within a paragraph become `<br />` tags
  - All `\n` and `\r` characters are removed from final HTML
- Sender name configured in `libs/google_operations.py` (`SENDER_NAME` constant)
- Uses Gmail API with `https://mail.google.com/` scope
- Daily sending limit applies (~1,500 messages for regular Gmail)
- For multi-line emails with proper formatting, use `--body-file` instead of `--body` to avoid newline escaping issues in shell commands

## Further Documentation

For comprehensive parameter reference, error handling, security considerations, and troubleshooting, see:
`docs/send_email.md`