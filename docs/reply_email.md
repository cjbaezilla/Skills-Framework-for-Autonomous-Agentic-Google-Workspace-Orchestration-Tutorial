# Gmail API - Reply Email Parameter Reference

## Overview
This document provides a comprehensive reference for replying to emails using the Gmail API through the `reply_email()` function in `google_operations.py` and its CLI wrapper `reply_email.py`.

## Basic Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `message_id` | string | Gmail message ID of the original email to reply to (required) |
| `body_html` | string | Reply body content (required) |

## Function Signature

```python
def reply_email(message_id, body_html, cc=None):
    """Reply to an existing email thread using Gmail API

    Args:
        message_id: Gmail message ID of the original email to reply to (string)
        body_html: Email reply body content in plain text (will be converted to HTML)
        cc: CC recipient email address(es) as comma-separated string (optional)

    Returns:
        str: Message ID if reply sent successfully, None on failure

    Note: This function automatically sets In-Reply-To and References headers
    and uses threadId to maintain proper email threading in Gmail.
    """
```

## Email Threading

The `reply_email()` function maintains proper email threading by automatically:

1. **Fetching original message** to extract headers:
   - `Message-ID` for threading
   - `Subject` (preserved unchanged)
   - `From` (set as reply recipient)
   - `Thread-ID` (for Gmail's threading model)

2. **Setting reply headers** in the outgoing message:
   - `In-Reply-To`: Original Message-ID
   - `References`: Original Message-ID
   - `Subject`: Preserved from original (not modified with "Re:" - Gmail handles this automatically)

3. **Using Gmail API correctly**:
   - Sends via `users.messages.send()` with `threadId` parameter
   - Ensures reply appears in the same conversation thread in Gmail UI
   - Maintains chronological order within the thread

## Return Value

- **Success**: Returns the Gmail message ID (string) for tracking and reference
- **Failure**: Returns `None` and prints an error to stderr

The CLI wrapper translates the return value to:
- Exit code 0 with success message on stdout: `Reply sent successfully! ID: <message_id>`
- Exit code 1 with error message on stderr: `Failed to send reply`

## Email Composition

### Signature Support

The reply-email skill includes automatic HTML signature appending on all replies. All replies are sent as HTML format with proper formatting.

**Configuration** (in `libs/google_operations.py`):

```python
# HTML signature file
SIGNATURE_HTML_FILE = "resources/signature.html"
```

**Behavior:**
- Replies are always sent as **HTML** format
- HTML signature is automatically appended to the reply body
- The body text is automatically converted from plain text to HTML (newlines become `<br>` tags)
- Signature appears after the reply content

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
# Line 16:
SENDER_NAME = "Augustus Machine"  # Change this
```

Or set to empty string to use Gmail default:
```python
SENDER_NAME = ""
```

### HTML-only format (NO plain text alternative - STRICT)

- **STRICT HTML-ONLY POLICY**: All replies are sent as **pure HTML single-part messages**
- Uses `MIMEText` with subtype 'html' ONLY - never creates multipart/alternative messages
- **No plain text part is ever added** - recipients without HTML capability may see blank content
- The body content is automatically converted to HTML:
  - Paragraphs are created from blocks of text separated by blank lines (double newlines)
  - Each paragraph is wrapped in `<p>` tags
  - Line breaks within paragraphs use `<br />` tags
  - Special characters are escaped to prevent HTML injection
- HTML signature is automatically appended to the reply body
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

Full Gmail access is required to send replies.

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
3. Proceed with reply sending

**Note**: The authorization flow requires a browser and user interaction. For headless/automated environments, use service accounts (requires additional configuration).

## Complete Working Examples

### Simple Technical Reply
```bash
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "The capital of Chile is Santiago. It's located in the central valley."
```

### Multi-line Reply with Formatting
```bash
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "Hello,

Thanks for your question about the project timeline.

Here's the current status:
• Phase 1: Complete (100%)
• Phase 2: In progress (65%)
• Phase 3: Planning stage

I'll send a detailed report by Friday.

Best regards,
Augustus Machine"
```

### Reply with CC Recipients
```bash
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "I've forwarded this to the team for review. We'll respond shortly." \
  --cc "manager@example.com,team@example.com"
```

### Using Body File for Complex Formatting
Create a file `technical_response.txt`:
```
Hi there,

Regarding your technical questions:

1. API Status: All endpoints are operational (99.9% uptime)
2. Rate Limits: 1000 requests/hour per API key
3. Documentation: https://api.example.com/docs

For urgent issues, contact support@example.com.

Regards,
Support Team
```

Then send:
```bash
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body-file "technical_response.txt"
```

### Integration in Python Scripts
```python
import subprocess

# Get message ID from previous email listing
message_id = "19d275345e8b1a8d"

result = subprocess.run([
    'python', 'scripts/google/reply_email.py',
    '--message-id', message_id,
    '--body', 'Thank you for your email. Your request has been processed.'
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"Reply sent: {result.stdout}")
else:
    print(f"Reply failed: {result.stderr}")
```

### Programmatic Usage (Direct Import)
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from google_operations import reply_email

# Reply to an email
email_id = reply_email(
    message_id='19d275345e8b1a8d',
    body_html='Thank you for reaching out. I\'ll respond with the details shortly.',
    cc='manager@example.com'  # optional
)

if email_id:
    print(f"Reply delivered! Message ID: {email_id}")
    # You can use this ID to track, modify, or delete the reply later
else:
    print("Reply delivery failed")
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Could not import google_operations` | Missing dependencies or wrong path | Ensure libs directory is in Python path and google_operations.py exists |
| `Gmail service not available` | Authentication failed or credentials missing | Run the script to trigger OAuth flow, verify credentials file exists |
| `Original message has no From header` | Corrupted or malformed original email | Verify the message_id points to a valid email |
| `HTTP error` | API quota exceeded, invalid message_id, etc. | Check error details in stderr, verify message_id, check Gmail API quota |
| `Token refresh failed` | Token expired and cannot be refreshed | Delete `google_token.json` to force re-authorization |

### Exit Codes
- `0`: Success (reply sent)
- `1`: Failure (any error condition)

## Security Considerations

- **Credentials**: Never commit `google_credentials.json` or `google_token.json` to version control
- **Token Storage**: `google_token.json` contains refresh tokens and should be kept secure
- **Least Privilege**: The OAuth scope grants full Gmail access. Only grant to trusted applications.
- **Input Validation**: The CLI does not validate email addresses; ensure input is sanitized to avoid injection attacks
- **Rate Limits**: Gmail API has daily sending limits (typically 1,500-2,000 messages/day for regular accounts)
- **Thread Integrity**: The reply script automatically threads correctly, but be cautious when replying programmatically to avoid spamming

## Gmail API Details

### Message ID Format
Returned message IDs are Base64URL-encoded strings, e.g.:
```
19d2766062052f4b
```

These IDs can be used with other Gmail API operations (get, delete, modify).

### Threading Best Practices

Gmail threading relies on:
1. **Message-ID header** in the original email (must exist)
2. **In-Reply-To header** in the reply (must match original Message-ID)
3. **References header** (should contain Message-ID chain)
4. **Subject** (typically preserved, though Gmail ignores minor variations)
5. **threadId** parameter (ensures both messages in same thread)

Our implementation handles all of these automatically.

### API Quotas
- **Daily sending limit**: ~1,500 messages for regular Gmail accounts, ~2,000 for Workspace accounts
- **Message size limit**: 25MB (including attachments - not supported by this basic version)
- **Recipient limit**: Up to 500 recipients per message (via multiple `to` addresses - not implemented in basic version)

### Rate Limiting
If you encounter `HttpError 429` (rate limit exceeded):
- Implement exponential backoff in your calling code
- Reduce sending frequency
- Request quota increase from Google if needed

## Troubleshooting

### Reply Not Appearing in Thread

If your reply doesn't appear in the same conversation:

1. **Check original Message-ID**: Ensure the original email has a Message-ID header (most do)
2. **Verify threading headers**: Use Gmail's "Show original" to inspect In-Reply-To and References
3. **Thread ID**: Confirm the threadId parameter was sent (check API response)

### Signature Issues

If signature is not appearing in received replies:

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
python scripts/google/reply_email.py --message-id "test" --body "test"
```

### Import Errors
Ensure the script is run from the project root (or adjust paths):
```bash
cd /path/to/project/root
python scripts/google/reply_email.py --message-id "xxx" --body "test"
```

### Missing Dependencies
Install required packages:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Getting the Message ID

To find a message ID to reply to:

**Using read-email skill:**
```bash
# List unread emails with IDs
python scripts/google/read_email.py --list

# Output shows:
# ID: 19d275345e8b1a8d
# From: sender@example.com
# Subject: Your question
```

**From Gmail web interface:**
1. Open the email
2. Click "More" (three dots) → "Show original"
3. Look for "Message-ID:" in the headers
4. Copy the value (may be in angle brackets)

**Programmatically:**
```python
from google_operations import list_unread_emails
emails = list_unread_emails(max_results=5)
for email in emails:
    print(f"ID: {email['id']}, Subject: {email['subject']}")
```

## Advanced Usage

### Customizing Sender Name
Edit `libs/google_operations.py`:
```python
# Line 16:
SENDER_NAME = "Your Custom Name"  # Change this
```

Or set to empty string to use Gmail default:
```python
SENDER_NAME = ""
```

### Bulk Reply Pattern
For replying to multiple emails:

```python
import time
from google_operations import reply_email, list_unread_emails

# Get all unread emails
unread = list_unread_emails(max_results=20)

for email in unread:
    message_id = email['id']
    subject = email['subject']
    sender = email['from']

    # Customize reply based on email content
    reply_body = f"Thanks for your email about '{subject}'. We'll respond shortly."

    success = reply_email(
        message_id=message_id,
        body_html=reply_body
    )

    if success:
        print(f"Replied to {sender} (ID: {message_id})")
    else:
        print(f"Failed to reply to {sender}")

    time.sleep(1)  # Rate limiting mitigation
```

### Conditional Replies with CC

```python
def smart_reply(message_id, subject, sender):
    """Send different replies based on subject or sender"""

    if "urgent" in subject.lower():
        reply_body = "We've received your urgent request and will respond within 2 hours."
        cc = "support-manager@example.com"
    elif "invoice" in subject.lower():
        reply_body = "Your invoice request has been received. Our billing team will contact you."
        cc = "billing@example.com"
    else:
        reply_body = "Thank you for your email. We'll get back to you within 24 hours."
        cc = None

    return reply_email(
        message_id=message_id,
        body_html=reply_body,
        cc=cc
    )
```

## Newline Handling and Multi-line Content

The `--body` parameter accepts multi-line content directly with actual line breaks. Do NOT use `\n` or `\r` escape sequences. The reply composer automatically converts your text into properly formatted HTML:

- **Blank lines** (two consecutive newlines) create separate paragraphs wrapped in `<p>` tags
- **Single newlines** within a paragraph become `<br />` tags for line breaks
- All newlines are removed from the final HTML content; only HTML tags remain

```bash
# ✅ CORRECT - Use actual line breaks in the body string
# This creates two paragraphs with a line break between them
python scripts/google/reply_email.py \
  --message-id "xxx" \
  --body "Hi there,

Thanks for your question.

We'll respond shortly."

# ❌ AVOID - Do not use \n escape sequences in shell commands
python scripts/google/reply_email.py \
  --message-id "xxx" \
  --body "Hi there,\n\nThanks for your question.\n\nWe'll respond shortly."

# Alternative: Use --body-file for complex formatting (recommended for multi-line)
echo "Hi there,

Thanks for your question.

We'll respond shortly." > reply.txt

python scripts/google/reply_email.py \
  --message-id "xxx" \
  --body-file "reply.txt"
```

## Differences from send_email

| Aspect | send_email | reply_email |
|--------|------------|-------------|
| Purpose | Send new email | Reply to existing email thread |
| Required params | `to`, `subject`, `body` | `message_id`, `body` |
| Recipient | Specified by `to` parameter | Automatically set to original sender |
| Subject | Specified by `subject` parameter | Automatically preserved from original |
| Threading | Creates new thread | Maintains existing thread |
| Headers | Standard new email headers | Adds In-Reply-To and References |
| API usage | `users.messages.send` | `users.messages.send` with `threadId` |

## See Also

- `google_operations.py:162` - `reply_email()` function implementation
- `reply_email.py` - CLI wrapper script
- `send_email.md` - Documentation for sending new emails
- `read_email.md` - Documentation for reading emails
- Gmail API Reference: https://developers.google.com/gmail/api/v1/reference/users/messages/send
- Threading in Gmail: https://developers.google.com/gmail/api/guides/threading
- OAuth 2.0 for Google APIs: https://developers.google.com/identity/protocols/oauth2
- HTML Email Best Practices: https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/Email

## CLI Usage

```bash
$ python reply_email.py --help

usage: reply_email.py [-h] --message-id MESSAGE_ID [--cc CC]
                      [--body BODY | --body-file BODY_FILE]

Reply to an email using Gmail

options:
  -h, --help            show this help message and exit
  --message-id MESSAGE_ID
                        Gmail message ID of the email to reply to
  --body BODY           Email reply body content (inline)
  --body-file BODY_FILE
                        Path to file containing reply body (preserves formatting)
  --cc CC               CC recipient email address(es), comma-separated
```