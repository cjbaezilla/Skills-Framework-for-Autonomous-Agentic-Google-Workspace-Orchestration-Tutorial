# Gmail API - Send Email Parameter Reference

## Overview
This document provides a comprehensive reference for sending emails using the Gmail API through the `send_email()` function in `google_operations.py` and its CLI wrapper `send_email.py`.

## Basic Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `to` | string | Recipient email address (required) |
| `subject` | string | Email subject line (required) |

## Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cc` | string | CC recipient email address(es), comma-separated (optional) |

## Body Parameters (exactly one required)

Either `--body` or `--body-file` must be provided:

| Parameter | Type | Description |
|-----------|------|-------------|
| `--body` | string | Email body content (sent as HTML only, no plain text alternative) |
| `--body-file` | string | Path to file containing email body (sent as HTML only, no plain text alternative) |

**HTML-ONLY FORMAT**: All emails are sent exclusively in HTML format with no plain text alternative. The input is plain text which gets automatically converted to HTML with proper escaping, line break conversion, and signature appending.

## Function Signature

```python
def send_email(to, subject, body_html, cc=None):
    """Send an email in HTML-only format with HTML signature (no plain text)
    
    Args:
        to: Recipient email address string
        subject: Email subject line string
        body_html: Email body content string (plain text input, converted to HTML)
        cc: CC recipient email address(es) as comma-separated string (optional)
    
    Returns:
        str: Message ID if sent successfully, None on failure
    
    Note: This function ALWAYS creates HTML-only MIME messages (MIMEText with subtype 'html').
    No multipart/alternative or plain text parts are ever added.
    ```

## Return Value

- **Success**: Returns the Gmail message ID (string) for tracking and reference
- **Failure**: Returns `None` and prints an error to stderr

The CLI wrapper translates the return value to:
- Exit code 0 with success message on stdout: `Email sent successfully! ID: <message_id>`
- Exit code 1 with error message on stderr: `Failed to send email`

## Email Composition

### Signature Support

The send-email skill includes automatic HTML signature appending on all emails. All emails are sent as HTML format with proper formatting.

**Configuration** (in `libs/google_operations.py`):

```python
# HTML signature file
SIGNATURE_HTML_FILE = "resources/signature.html"
```

**Behavior:**
- Emails are always sent as **HTML** format
- HTML signature is automatically appended to the email body
- The body text is automatically converted from plain text to HTML (newlines become `<br>` tags)

**HTML Signature Formatting:**
```html
<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
<p>Best regards,</p>
<p><strong>Augustus Machine</strong><br>
<a href="https://example.com">example.com</a></p>
</div>
```

### From Address
The sender is determined automatically:
1. If `SENDER_NAME` is set in `google_operations.py` and the authenticated user's email can be retrieved, the format is:
   ```
   "SENDER_NAME <user@gmail.com>"
   ```
2. If only `SENDER_NAME` is set (cannot retrieve email):
   ```
   "SENDER_NAME"
   ```
3. If `SENDER_NAME` is empty, Gmail uses the default account name.

**Configuration**: Edit the `SENDER_NAME` constant in `libs/google_operations.py`:
```python
SENDER_NAME = "Augustus Machine"  # Your display name
```

### HTML-only format (NO plain text alternative - STRICT)
- **STRICT HTML-ONLY POLICY**: All emails are sent as **pure HTML single-part messages**
- Uses `MIMEText` with subtype 'html' ONLY - never creates multipart/alternative messages
- **No plain text part is ever added** - recipients without HTML capability may see blank content
- The body content is automatically converted to HTML:
  - Paragraphs are created from blocks of text separated by blank lines (double newlines)
  - Each paragraph is wrapped in `<p>` tags
  - Line breaks within paragraphs use `<br />` tags
  - Special characters are escaped to prevent HTML injection
- HTML signature is automatically appended to the email body
- Character encoding: UTF-8
- Line endings in final HTML: LF (Unix-style) for clean MIME construction
- **No `\n` or `\r` characters appear in the final HTML body content**

## Authentication & Authorization

### OAuth 2.0 Scopes
The application requests the following scopes:
```
https://mail.google.com/
https://www.googleapis.com/auth/calendar
```

Full Gmail access is required to send emails.

### Credential Files
- **Client Secrets**: `credentials/google_credentials.json`
  - Download from Google Cloud Console (OAuth 2.0 Client ID)
- **Token Cache**: `credentials/google_token.json`
  - Auto-generated on first authorization
  - Contains refresh token for automatic token renewal

### First-Time Authorization
On first run or when token expires, the script will:
1. Open a browser window for user consent
2. Generate a new token and save to `google_token.json`
3. Proceed with email sending

**Note**: The authorization flow requires a browser and user interaction. For headless/automated environments, use service accounts (requires additional configuration).

## Complete Working Examples

### Basic Email
```bash
python scripts/google/send_email.py \
  --to "colleague@example.com" \
  --subject "Project Status Update" \
  --body "The project is progressing well. We're on track for the Q2 deadline."
```

### Automated Notification
```bash
python scripts/google/send_email.py \
  --to "alerts@example.com" \
  --subject "⚠️ System Alert: High CPU Usage" \
  --body "Server production-web-01 has exceeded 90% CPU usage for the last 15 minutes."
```

### Multi-line Email (using body-file)
Create a file `email_body.txt`:
```
Hello Team,

The project status update is as follows:

• Design phase: Complete
• Development: 75% complete
• Testing: Scheduled for next week

Please review the attached documents.

Best regards,
Project Manager
```

Then send:
```bash
python scripts/google/send_email.py \
  --to "team@example.com" \
  --subject "Weekly Project Update" \
  --body-file "email_body.txt"
```

### Integration with Scripts
```python
import subprocess

result = subprocess.run([
    'python', 'scripts/google/send_email.py',
    '--to', 'team@example.com',
    '--subject', 'Daily Report Ready',
    '--body', 'The daily analytics report has been generated and is available at: https://example.com/reports/daily.pdf'
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"Notification sent: {result.stdout}")
else:
    print(f"Failed to send: {result.stderr}")
```

### Programmatic Usage (Direct Import)
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from google_operations import send_email

email_id = send_email(
    to='recipient@example.com',
    subject='Hello from Python',
    body_text='This email was sent by calling send_email() directly.'
)

if email_id:
    print(f"Email delivered! Message ID: {email_id}")
else:
    print("Delivery failed")
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Could not import google_operations` | Missing dependencies or wrong path | Ensure libs directory is in Python path and google_operations.py exists |
| `Gmail service not available` | Authentication failed or credentials missing | Run the script to trigger OAuth flow, verify credentials file exists |
| `HTTP error` | API quota exceeded, invalid recipient, etc. | Check error details in stderr, verify recipient address, check Gmail API quota |
| `Token refresh failed` | Token expired and cannot be refreshed | Delete `google_token.json` to force re-authorization |

### Exit Codes
- `0`: Success (email sent)
- `1`: Failure (any error condition)

## Security Considerations

- **Credentials**: Never commit `google_credentials.json` or `google_token.json` to version control
- **Token Storage**: `google_token.json` contains refresh tokens and should be kept secure
- **Least Privilege**: The OAuth scope grants full Gmail access. Only grant to trusted applications.
- **Input Validation**: The CLI does not validate email addresses; ensure input is sanitized to avoid injection attacks
- **Rate Limits**: Gmail API has daily sending limits (typically 1,500-2,000 messages/day for regular accounts)

## Gmail API Details

### Message ID Format
Returned message IDs are Base64URL-encoded strings, e.g.:
```
16e8b1fexample1234567890abcdef
```

These IDs can be used with other Gmail API operations (get, delete, modify).

### API Quotas
- **Daily sending limit**: ~1,500 messages for regular Gmail accounts, ~2,000 for Workspace accounts
- **Message size limit**: 25MB (including attachments - not supported by this basic version)
- **Recipient limit**: Up to 500 recipients per message (via multiple `to` addresses - not implemented in basic version)

### Rate Limiting
If you encounter `HttpError 429` (rate limit exceeded):
- Implement exponential backoff in your calling code
- Reduce sending frequency
- Request quota increase from Google if needed

## Advanced Usage

### Customizing Sender Name
Edit `libs/google_operations.py`:
```python
# Line 14:
SENDER_NAME = "Your Custom Name"  # Change this
```

Or set to empty string to use Gmail default:
```python
SENDER_NAME = ""
```

### Bulk Sending Pattern
For sending multiple emails efficiently:

```python
import time
from google_operations import send_email

recipients = ['a@example.com', 'b@example.com', 'c@example.com']
subject = "Newsletter"

for email in recipients:
    success = send_email(
        to=email,
        subject=subject,
        body_text=f"Hello {email}, here's our update..."
    )
    if success:
        print(f"Sent to {email}")
    else:
        print(f"Failed for {email}")

    time.sleep(1)  # Rate limiting mitigation
```

## Troubleshooting

### Signature Issues

If signature is not appearing in received emails:

1. **Verify configuration**: Ensure `SIGNATURE_HTML_FILE` is set in `google_operations.py`
2. **Check file path**: The signature file must exist at the specified path
3. **Check file content**: Ensure the signature file is not empty
4. **Inspect raw email**: Use Gmail's "Show original" to verify the signature is present in the raw MIME message

### Credential Issues
If you see:
```
[ERROR] Failed to authenticate
```
Delete the token and re-authorize:
```bash
rm credentials/google_token.json
python scripts/google/send_email.py --to "you@example.com" --subject "test" --body "test"
```

### Import Errors
Ensure the script is run from the project root (or adjust paths):
```bash
cd /path/to/project/root
python scripts/google/send_email.py ...
```

### Missing Dependencies
Install required packages:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Newline Handling and Multi-line Content

The `--body` parameter accepts multi-line content directly with actual line breaks. Do NOT use `\n` or `\r` escape sequences. The email composer automatically converts your text into properly formatted HTML:

- **Blank lines** (two consecutive newlines) create separate paragraphs wrapped in `<p>` tags
- **Single newlines** within a paragraph become `<br />` tags for line breaks
- All newlines are removed from the final HTML content; only HTML tags remain

```bash
# ✅ CORRECT - Use actual line breaks in the body string
# This creates two paragraphs with a line break between them
python scripts/google/send_email.py --to "user@example.com" --subject "Meeting" --body "Hi there,

Let's meet tomorrow at 3 PM.

Best regards"

# ❌ AVOID - Do not use \n escape sequences in shell commands
python scripts/google/send_email.py --to "user@example.com" --subject "Meeting" --body "Hi there,\n\nLet's meet tomorrow at 3 PM.\n\nBest regards"

# Alternative: Use --body-file for complex formatting (recommended for multi-line)
echo "Hi there,

Let's meet tomorrow at 3 PM.

Best regards" > body.txt
python scripts/google/send_email.py --to "user@example.com" --subject "Meeting" --body-file "body.txt"
```

**HTML Conversion Example:**

Input text:
```
Hello Team,

Project update:
- Phase 1: Complete
- Phase 2: In progress

Review the documents.

Best,
Manager
```

Becomes:
```html
<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">
<p>Hello Team,</p>
<p>Project update:<br />
- Phase 1: Complete<br />
- Phase 2: In progress</p>
<p>Review the documents.</p>
<p>Best,<br />
Manager</p>
</div>
```

## See Also

- `google_operations.py:149` - `send_email()` function implementation
- `send_email.py` - CLI wrapper script
- Gmail API Reference: https://developers.google.com/gmail/api/v1/reference/users/messages/send
- OAuth 2.0 for Google APIs: https://developers.google.com/identity/protocols/oauth2

## CLI Usage

$ python send_email.py --help

usage: send_email.py [-h] --to TO [--cc CC] --subject SUBJECT [--body BODY | --body-file BODY_FILE]

Send an email using Gmail

options:
  -h, --help            show this help message and exit
  --to TO               Recipient email address
  --cc CC               CC recipient email address(es), comma-separated
  --subject SUBJECT     Email subject
  --body BODY           Email body text (inline)
  --body-file BODY_FILE
                        Path to file containing email body (preserves formatting)