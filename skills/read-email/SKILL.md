---
name: read-email
description: Reads emails from Gmail inbox using the Google Gmail API with list and read capabilities
license: MIT
compatibility: opencode
metadata:
  category: google-workspace
  audience: developers, productivity-users
  script: read_email.py
---

## What I do

I read emails via Gmail using the Google Gmail API. My capabilities include:

- Listing unread emails with subject, sender, and snippet preview
- Reading full email content (subject, from, body) by message ID
- Configurable output format (text or JSON)
- Flexible result limits for listing
- Cached authentication with automatic token refresh
- Clean error reporting and exit codes
- Integration with Google's OAuth 2.0 flow

## When to use me

Use me when you need to:

- Check your inbox programmatically
- Monitor unread emails
- Retrieve email content for processing
- Integrate email reading into automation workflows
- Debug email-related issues
- Bulk process incoming messages

## How to invoke me

```
python scripts/google/read_email.py --list [--max-results N] [--format text|json]
```

```
python scripts/google/read_email.py --message-id <MESSAGE_ID> [--format text|json]
```

## Parameters

**Actions (one required):**

- `--list`: List unread emails (default if no action specified)
- `--message-id`: Read a specific email by its Gmail message ID

**Optional:**

- `--max-results`: Maximum number of emails to list (default: 10, applies only with --list)
- `--format`: Output format - 'text' (human-readable) or 'json' (machine-readable). Default: text

## Return values

On success:
- Exit code `0`
- Output varies by format and action

On failure:
- Exit code `1`
- Error message printed to stderr

## Example usage

```bash
# List 5 unread emails (default is 10)
python scripts/google/read_email.py --list --max-results 5

# List unread emails in JSON format for programmatic processing
python scripts/google/read_email.py --list --format json

# Read a specific email by message ID
python scripts/google/read_email.py --message-id "17c3a5b6f7e8a9b0c1d2e3f4"

# Read email and get output as JSON
python scripts/google/read_email.py --message-id "17c3a5b6f7e8a9b0c1d2e3f4" --format json
```

## Notes

- Requires Google OAuth credentials in `credentials/`
   - `google_credentials.json` (OAuth client secrets)
   - `google_token.json` (auto-generated on first run)
- First execution opens browser for authorization
- Uses Gmail API with `https://mail.google.com/` scope
- Email body is truncated to 2000 characters for safety in text format
- For --list, returns: message ID, sender, subject, and snippet preview
- For --message-id, returns: full email with subject, from, and body

## Further Documentation

For comprehensive parameter reference, error handling, and troubleshooting, see:
`docs/list_read_email.md`