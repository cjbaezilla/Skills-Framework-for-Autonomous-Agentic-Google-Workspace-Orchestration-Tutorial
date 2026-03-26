# Gmail API - Read Email Parameter Reference

## Overview
This document provides a comprehensive reference for reading emails using the Gmail API v1 through the `list_unread_emails()` and `get_email_content()` functions in `google_operations.py` and their CLI wrapper `read_email.py`.

## Actions

| Action | Required | Description |
|--------|----------|-------------|
| `--list` | No (default) | List unread emails with metadata |
| `--message-id` | No | Read full content of a specific email |

## Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `--max-results` | integer | Maximum number of emails to list (default: 10, applies only with --list) |
| `--format` | string | Output format: 'text' (human-readable) or 'json' (machine-readable). Default: text |

## Function Signatures

### list_unread_emails

```python
def list_unread_emails(max_results=10):
    """Returns list of unread emails (subject, sender, snippet, id)"""
```

**Parameters:**
- `max_results` (int, optional): Maximum number of unread emails to retrieve (default: 10)

**Returns:**
- List of dictionaries with keys: `id`, `subject`, `from`, `snippet`

### get_email_content

```python
def get_email_content(message_id):
    """Get full email: subject, from, body (plain text)"""
```

**Parameters:**
- `message_id` (string, required): Gmail message ID

**Returns:**
- Dictionary with keys: `id`, `subject`, `from`, `body` (truncated to 2000 characters for safety)

## Return Value

### CLI Exit Codes

- `0`: Success
- `1`: Failure (authentication error, network error, invalid message ID, etc.)

### Output Formats

**Text format (--format text):**

List mode:
```
Found X unread email(s):
--------------------------------------------------------------------------------
1. ID: 17c3a5b6f7e8a9b0c1d2e3f4
   From: John Doe <john@example.com>
   Subject: Project Update
   Snippet: Hi team, I wanted to provide an update on the current sprint...
```

Read mode:
```
ID: 17c3a5b6f7e8a9b0c1d2e3f4
From: John Doe <john@example.com>
Subject: Project Update

Body:
Hi team,

I wanted to provide an update on the current sprint progress...

Best regards,
John
```

**JSON format (--format json):**

```json
[
  {
    "id": "17c3a5b6f7e8a9b0c1d2e3f4",
    "from": "John Doe <john@example.com>",
    "subject": "Project Update",
    "snippet": "Hi team, I wanted to provide an update..."
  }
]
```

```json
{
  "id": "17c3a5b6f7e8a9b0c1d2e3f4",
  "from": "John Doe <john@example.com>",
  "subject": "Project Update",
  "body": "Hi team,\n\nI wanted to provide an update on the current sprint progress...\n\nBest regards,\nJohn"
}
```

## Authentication & Authorization

### OAuth 2.0 Scopes
The application requests the following scopes:
```
https://mail.google.com/
https://www.googleapis.com/auth/calendar
```

Full Gmail access is required to read emails.

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
3. Proceed with email reading

**Note**: The authorization flow requires a browser and user interaction.

## Complete Working Examples

### List Unread Emails (Text Format)
```bash
python scripts/google/read_email.py --list --max-results 5
```

Output:
```
Found 3 unread email(s):
--------------------------------------------------------------------------------
1. ID: 17c3a5b6f7e8a9b0c1d2e3f4
   From: John Doe <john@example.com>
   Subject: Project Update
   Snippet: Hi team, I wanted to provide an update on the current sprint progress...

2. ID: 18d4b6c7g8f9h0i1j2k3l4m
   From: Jane Smith <jane@example.com>
   Subject: Meeting Notes
   Snippet: Here are the notes from yesterday's meeting...

3. ID: 19e5c7d8h9i0j1k2l3m4n5o
   From: GitHub <noreply@github.com>
   Subject: [GitHub] Security alert
   Snippet: A security vulnerability has been identified in one of your dependencies...
```

### List Unread Emails (JSON Format for Automation)
```bash
python scripts/google/read_email.py --list --max-results 10 --format json
```

Useful for piping to other tools:
```bash
# Get IDs of first 5 unread emails
python scripts/google/read_email.py --list --max-results 5 --format json | jq -r '.[].id'
```

### Read Specific Email by Message ID
```bash
python scripts/google/read_email.py --message-id "17c3a5b6f7e8a9b0c1d2e3f4"
```

Output:
```
ID: 17c3a5b6f7e8a9b0c1d2e3f4
From: John Doe <john@example.com>
Subject: Project Update

Body:
Hi team,

I wanted to provide an update on the current sprint progress. We're currently 75% complete with the development phase, and testing is scheduled to begin next week.

Key accomplishments:
- Backend API completed
- Database schema finalized
- Initial frontend components built

Next steps:
- Complete UI/UX refinement
- Begin integration testing
- Prepare deployment scripts

Please let me know if you have any questions.

Best regards,
John
Project Manager
```

### Read Email as JSON for Programmatic Processing
```bash
python scripts/google/read_email.py --message-id "17c3a5b6f7e8a9b0c1d2e3f4" --format json > email.json
```

### Integration with Shell Scripts
```bash
#!/bin/bash
# Monitor unread emails and extract sender information

EMAILS=$(python scripts/google/read_email.py --list --max-results 20 --format json)
echo "You have $(echo "$EMAILS" | jq length) unread emails"

# Extract unique senders
echo "Senders:"
echo "$EMAILS" | jq -r '.[].from' | sort | uniq -c | sort -nr
```

### Python Integration (Direct Import)
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from google_operations import list_unread_emails, get_email_content

# List unread emails
unread = list_unread_emails(max_results=5)
print(f"Found {len(unread)} unread emails:")
for email in unread:
    print(f"  - {email['subject']} from {email['from']}")

# Read specific email
if unread:
    email_id = unread[0]['id']
    full_email = get_email_content(email_id)
    print(f"\nFull email body:\n{full_email['body']}")
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Could not import google_operations` | Missing dependencies or wrong path | Ensure libs directory is in Python path and google_operations.py exists |
| `Gmail service not available` | Authentication failed or credentials missing | Run the script to trigger OAuth flow, verify credentials file exists |
| `Could not retrieve email with ID` | Invalid message ID or message deleted | Verify the message ID exists; Gmail IDs are persistent but can become invalid if deleted |
| `HTTP error` | API quota exceeded, network issue, etc. | Check error details in stderr, verify network connectivity, check Gmail API quota |

### Exit Codes
- `0`: Success
- `1`: Failure (any error condition)

## Security Considerations

- **Credentials**: Never commit `google_credentials.json` or `google_token.json` to version control
- **Token Storage**: `google_token.json` contains refresh tokens and should be kept secure
- **Least Privilege**: The OAuth scope grants full Gmail access. Only grant to trusted applications.
- **Message IDs**: Treat message IDs as sensitive information; they provide access to email content
- **Rate Limits**: Gmail API has read quotas (typically 1,000,000,000 queries/day) and per-user rate limits
- **Data Handling**: Email content may contain sensitive personal information; handle according to privacy policies

## Gmail API Details

### Message ID Format
Returned message IDs are Base64URL-encoded strings, e.g.:
```
17c3a5b6f7e8a9b0c1d2e3f4
```

These IDs are stable and can be used with other Gmail API operations.

### API Quotas
- **Read queries**: Up to 1,000,000,000 per day for standard Gmail accounts
- **Message size**: Response body limited to ~10MB for full message format
- **Rate limits**: Per-user limits apply (typically ~250 queries/second/user)
- **List operations**: `users.messages.list` returns up to 500 results per page (handled automatically)

### Email Body Extraction
The `get_email_content()` function extracts plain text from emails:
- Searches for `text/plain` MIME parts
- Decodes Base64URL-encoded content
- Returns UTF-8 decoded text
- Truncates to 2000 characters for safety (to prevent memory issues with very long emails)
- Does not handle HTML emails (only extracts plain text parts)

### Unread Email Detection
The `list_unread_emails()` function uses the Gmail `UNREAD` label:
- Only returns messages with the `UNREAD` system label
- Does not mark messages as read (preserves unread status)
- Sorted by arrival order (most recent first, according to Gmail default)

## Advanced Usage

### Processing All Unread Emails with Auto-Mark as Read Pattern
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from google_operations import list_unread_emails, get_email_content

def process_unread_emails():
    """Fetch and process all unread emails"""
    unread = list_unread_emails(max_results=100)  # Adjust as needed
    
    for email in unread:
        print(f"Processing: {email['subject']}")
        full = get_email_content(email['id'])
        
        # Your processing logic here
        process_email(full)
        
        # Optionally mark as read using Gmail API directly
        # (not implemented in google_operations.py by default)

def process_email(email_data):
    """Example processing function"""
    print(f"From: {email_data['from']}")
    print(f"Body preview: {email_data['body'][:200]}...")
```

### Batch Processing with Result Limits
```bash
# Process emails in batches to avoid rate limits
for i in {1..5}; do
    echo "Batch $i:"
    python scripts/google/read_email.py --list --max-results 20 --format json | jq -r '.[].subject'
    sleep 1  # Rate limiting mitigation
done
```

### Filtering by Sender Domain (Using Gmail Search API)
The current `list_unread_emails()` doesn't support filtering. For advanced queries, use the search_emails() function from google_operations.py:

```python
from google_operations import search_emails

# Find unread emails from specific domain
results = search_emails(query="from:@example.com is:unread", max_results=10)
print(f"Found {len(results)} unread emails from example.com")
```

## Troubleshooting

### Authentication Issues

If you see authentication errors (e.g., `Gmail service not available`):

1. **Verify credentials exist**:
   ```bash
   ls -la credentials/google_credentials.json
   ```

2. **Delete cached token to force re-authorization**:
   ```bash
   rm credentials/google_token.json
   ```

3. **Run script to trigger OAuth flow**:
   ```bash
   python scripts/google/read_email.py --list
   ```
   A browser window should open for consent.

4. **Check OAuth consent screen**: Ensure your Google Cloud project has the Gmail API enabled and OAuth consent configured.

### Import Errors

If `Could not import google_operations`:
- Verify you're running from the project root directory
- Ensure `libs/google_operations.py` exists
- Ensure required Python packages are installed:
  ```bash
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
  ```

### Permission Denied

The OAuth scope `https://mail.google.com/` grants full access. If you see permission errors:
- Ensure the OAuth client in Google Cloud Console is configured for "External" or "Internal" as appropriate
- Verify your Google account is added as a test user if the app is in testing mode
- Check that the Gmail API is enabled in the Google Cloud project

### HTTP Errors

Common HTTP errors from Gmail API:
- `403 Quota exceeded`: Daily read quota limit reached (unlikely, but possible)
- `401 Invalid Credentials`: Token expired or invalid - delete and re-authorize
- `404 Not Found`: Message ID doesn't exist or has been deleted
- `429 Too Many Requests`: Rate limit exceeded - implement exponential backoff

### Message Body Empty or Truncated

- Emails may be truncated to 2000 characters (safety limit in `get_email_content()`)
- HTML-only emails may have no plain text part; consider extending `get_email_content()` to extract HTML as well

### No Unread Emails Found

- Verify you actually have unread emails in your Gmail inbox
- Check that you're using the correct Google account (token is account-specific)
- The `UNREAD` label may have been manually removed from messages

## See Also

- `list_unread_emails()` - lists unread email metadata in google_operations.py:110
- `get_email_content()` - retrieves full email content in google_operations.py:137
- `search_emails()` - advanced search with Gmail query syntax in google_operations.py:130
- Gmail API Reference: https://developers.google.com/gmail/api/v1/reference/users/messages
- OAuth 2.0 for Google APIs: https://developers.google.com/identity/protocols/oauth2

## CLI Usage

$ python read_email.py --help

usage: read_email.py [-h] [--list] [--max-results MAX_RESULTS] [--message-id MESSAGE_ID] [--format {text,json}]

Read emails from Gmail inbox

options:
  -h, --help            show this help message and exit
  --list                List unread emails (default if no action specified)
  --max-results MAX_RESULTS
                        Maximum number of emails to list (default: 10)
  --message-id MESSAGE_ID
                        Read specific email by message ID
  --format {text,json}  Output format (default: text)