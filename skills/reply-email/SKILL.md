---
name: reply-email
description: Replies to existing emails using the Google Gmail API with proper threading support
license: MIT
compatibility: opencode
metadata:
  category: google-workspace
  audience: developers, productivity-users
  script: reply_email.py
---

## What I do

I reply to emails via Gmail using the Google Gmail API. My capabilities include:

- Replying to specific emails by message ID
- Proper email threading (sets In-Reply-To and References headers)
- Maintains conversation continuity in Gmail
- Thread-aware sending (uses threadId parameter)
- HTML-only format with automatic signature appending
- Optional CC recipients
- Cached authentication with automatic token refresh
- Clean error reporting and exit codes
- Integration with Google's OAuth 2.0 flow

## When to use me

Use me when you need to:

- Respond to incoming emails programmatically
- Send automated replies that appear as proper email conversations
- Build email automation workflows that maintain threading
- Create chatbots or assistants that interact via email
- Process and respond to notifications or alerts
- Integrate email response capabilities into automated systems

## How to invoke me

```
python scripts/google/reply_email.py --message-id <MESSAGE_ID> --body <BODY_CONTENT>
```

```
python scripts/google/reply_email.py --message-id <MESSAGE_ID> --body-file <FILE_PATH>
```

## Parameters

**Required:**

- `--message-id`: Gmail message ID of the email to reply to (string)
- Either `--body` OR `--body-file` (exactly one required)

**Optional:**

- `--cc`: CC recipient email address(es), comma-separated (string)

**Body (exactly one required):**

- `--body`: Email reply body content (string) - Accepts multi-line content with actual line breaks. Text is automatically converted to HTML: blank lines become `<p>` paragraphs, single newlines become `<br />` tags. **Sent as HTML only**.
- `--body-file`: Path to a text file containing the email body - Use for multi-line content, preserving line breaks and formatting. Text is automatically converted to HTML: blank lines become `<p>` paragraphs, single newlines become `<br />` tags. **Sent as HTML only**.

**HTML-ONLY POLICY**: This skill sends replies **exclusively in HTML format** with no plain text alternative. The body content (whether from `--body` or `--body-file`) is automatically converted to HTML: blank lines become `<p>` paragraphs, single newlines become `<br />` tags, and special characters are escaped. **No `\n` or `\r` characters appear in the final HTML output**.

## Return values

On success:
- Exit code `0`
- Output: `Reply sent successfully! ID: <message_id>`

On failure:
- Exit code `1`
- Error message printed to stderr

## Example usage

```bash
# Simple reply
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "Thank you for your email. I'll get back to you shortly."

# Reply with multi-line content (using actual newlines)
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "Hi there,

Thanks for reaching out. I'll review your question and respond by end of day.

Best regards,
Augustus"

# Reply with line breaks and formatting
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "Hello,

Here are the answers to your questions:

• Item 1: Yes, that's correct
• Item 2: The meeting is scheduled for 3 PM
• Item 3: I'll send the documents tomorrow

Let me know if you need anything else."

# Reply with body-file for complex formatting
echo "Hello Team,

The project status is:

• Phase 1: Complete (100%)
• Phase 2: In progress (75%)
• Phase 3: Planning stage

Review the attached specs.

Thanks,
Project Manager" > reply_body.txt

python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body-file "reply_body.txt"

# Reply with CC
python scripts/google/reply_email.py \
  --message-id "19d275345e8b1a8d" \
  --body "See my response below." \
  --cc "manager@example.com,team@example.com"
```

## Notes

- Requires Google OAuth credentials in `credentials/`
   - `google_credentials.json` (OAuth client secrets)
   - `google_token.json` (auto-generated on first run)
- First execution opens browser for authorization
- Uses Gmail API with `https://mail.google.com/` scope
- The reply maintains proper email threading by automatically setting:
  - `In-Reply-To` header (original Message-ID)
  - `References` header (original Message-ID)
  - `threadId` parameter in API call
- Subject is automatically preserved from the original message
- Recipient is automatically set to the original sender
- Email body is truncated to 2000 characters for safety in text format
- HTML signature is automatically appended (configure in `google_operations.py`)
- Sender name configured in `google_operations.py` (`SENDER_NAME` constant)

## Further Documentation

For comprehensive parameter reference, error handling, security considerations, and troubleshooting, see:
`docs/reply_email.md`

## See Also

- `google_operations.py:162` - `reply_email()` function implementation
- `reply_email.py` - CLI wrapper script
- Gmail API Reference: https://developers.google.com/gmail/api/v1/reference/users/messages/send
- OAuth 2.0 for Google APIs: https://developers.google.com/identity/protocols/oauth2
- Threading in Gmail: https://developers.google.com/gmail/api/guides/threading

Base directory for this skill: file:///D:/DEV/111-MASTER/skills/reply-email
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.
Note: file list is sampled.
