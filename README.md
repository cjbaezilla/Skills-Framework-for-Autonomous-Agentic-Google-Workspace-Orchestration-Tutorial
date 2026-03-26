# Skills Framework for Autonomous Agentic Google Workspace Orchestration

A comprehensive Python-based framework for integrating Google Workspace (Gmail & Calendar) with autonomous AI agent systems. This project demonstrates production-ready patterns for secure authentication, modular skill design, and orchestration of multi-step workflows.

## Overview

This repository provides a fully configured Google Workspace integration that enables AI agents to manage emails and calendar events programmatically. Built with security and extensibility in mind, it features:

- **4 distinct skills**: send-email, read-email, reply-email, create-calendar-event
- **OAuth 2.0 authentication** with automatic token refresh
- **Skill-based architecture** compatible with OpenCode agent systems
- **HTML-only email format** with automatic signature appending
- **Proper email threading** with In-Reply-To and References headers
- **Timezone-aware calendar events** with DST handling via pytz
- **Comprehensive documentation** including setup guide and API reference

## Architecture

```
├── libs/
│   └── google_operations.py     # Core library: authentication & API wrappers
├── scripts/google/
│   ├── send_email.py            # Send email CLI
│   ├── read_email.py            # Read/list emails CLI
│   ├── reply_email.py           # Reply to emails CLI (with threading)
│   └── create_calendar_event.py # Create calendar events CLI
├── skills/
│   ├── send-email/SKILL.md      # Skill specification for send-email
│   ├── read-email/SKILL.md      # Skill specification for read-email
│   ├── reply-email/SKILL.md     # Skill specification for reply-email
│   └── create-calendar-event/SKILL.md  # Skill specification for calendar
├── docs/
│   ├── send_email.md            # Detailed send-email reference
│   ├── list_read_email.md       # Detailed read-email reference
│   ├── reply_email.md           # Detailed reply-email reference
│   └── create_calendar_event.md # Detailed calendar reference
├── resources/
│   └── signature.html           # HTML email signature (configurable)
├── credentials/                 # OAuth credentials (create this locally)
│   ├── google_credentials.json  # Downloaded from Google Cloud Console
│   └── google_token.json        # Auto-generated on first auth (sensitive!)
├── quickstart_google_suite.py   # Bootstrap authentication script
└── article.md                   # Complete tutorial & conceptual guide
```

### Core Library (`libs/google_operations.py`)

All Google API interactions are centralized in this library:

- `get_gmail_service()` / `get_calendar_service()` - Auto-initialize, auto-refresh
- Email functions: `send_email()`, `list_unread_emails()`, `search_emails()`, `get_email_content()`, `reply_email()`
- Calendar functions: `list_calendars()`, `list_events()`, `get_event()`, `create_event()`, `update_event()`, `delete_event()`
- Configurable: `SENDER_NAME`, `SIGNATURE_HTML_FILE`

### Skill System

Each skill consists of:

1. **CLI script** (`scripts/google/*.py`) - Standalone command-line tool
2. **SKILL.md** (`skills/*/SKILL.md`) - Machine-parsable specification
3. **Optional docs** (`docs/*.md`) - Comprehensive reference

Skills declare their purpose, parameters, return values, and usage examples. AI agents read these specifications to discover capabilities and invoke them appropriately.

## Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Gmail and Calendar APIs enabled

### Installation

1. **Clone and navigate**
   ```bash
   cd "D:\DEV\Skills-Framework-for-Autonomous-Agentic-Google-Workspace-Orchestration-Tutorial"
   ```

2. **Install dependencies**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz
   ```

3. **Set up Google Cloud Project**

   Follow the step-by-step guide in `article.md` (sections 1-4):

   - Create a Google Cloud Project
   - Enable Gmail API and Google Calendar API
   - Configure OAuth consent screen (add test users)
   - Create OAuth 2.0 Desktop Client credentials
   - Download `credentials.json` → save as `credentials/google_credentials.json`

4. **Authenticate and obtain refresh token**

   ```bash
   python quickstart_google_suite.py
   ```

   This opens your browser, completes OAuth flow, and saves `credentials/google_token.json`.

5. **IMPORTANT: Publish your OAuth app for autonomous agents**

   Return to Google Cloud Console → OAuth consent screen → click **Publish App**.  
   Without this, refresh tokens expire after 7 days and break long-running agents.

### Verify Installation

Test each skill:

```bash
# Send a test email
python scripts/google/send_email.py --to "your-email@example.com" --subject "Test" --body "Hello from the framework!"

# List unread emails
python scripts/google/read_email.py --list --max-results 5

# Create a calendar event
python scripts/google/create_calendar_event.py --year 2026 --month 3 --day 30 --start-hour 14 --end-hour 16 --summary "Team Meeting" --attendees "colleague@example.com"
```

## Skill Reference

### 1. Send Email (`send-email`)

Sends HTML emails via Gmail with automatic signature.

```bash
python scripts/google/send_email.py --to "user@example.com" --subject "Report" --body "See attached."
python scripts/google/send_email.py --to "team@example.com" --cc "manager@example.com" --subject "Daily Update" --body-file "update.txt"
```

**Parameters**: `--to`, `--subject` (required); `--cc`, `--body`, `--body-file` (optional; exactly one body required).

**Returns**: Message ID on success (exit code 0).

**Notes**:
- Strictly HTML-only (no plain text alternative)
- HTML signature automatically appended
- `--body-file` recommended for multi-line content

**See**: `skills/send-email/SKILL.md` | `docs/send_email.md`

### 2. Read Email (`read-email`)

Lists unread emails or reads full message content.

```bash
# List unread emails
python scripts/google/read_email.py --list --max-results 10 --format json

# Read specific email
python scripts/google/read_email.py --message-id "17c3a5b6f7e8a9b0c1d2e3f4" --format text
```

**Parameters**: `--list` OR `--message-id` (required); `--max-results`, `--format` (optional).

**Returns**: Email metadata or full content.

**Notes**:
- Body truncated to 2000 characters in text format
- JSON format recommended for programmatic processing

**See**: `skills/read-email/SKILL.md` | `docs/list_read_email.md`

### 3. Reply Email (`reply-email`)

Replies to existing threads with proper formatting.

```bash
python scripts/google/reply_email.py --message-id "19d275345e8b1a8d" --body "Thank you, I'll review."
python scripts/google/reply_email.py --message-id "19d275345e8b1a8d" --body-file "reply.txt" --cc "manager@example.com"
```

**Parameters**: `--message-id`, body (`--body` or `--body-file`) (required); `--cc` (optional).

**Returns**: Reply message ID on success.

**Notes**:
- Maintains threading via In-Reply-To and References headers
- HTML-only with automatic signature
- Subject and recipient auto-populated from original message

**See**: `skills/reply-email/SKILL.md` | `docs/reply_email.md`

### 4. Create Calendar Event (`create-calendar-event`)

Creates events with timezone support.

```bash
python scripts/google/create_calendar_event.py \
  --year 2026 --month 3 --day 26 --start-hour 15 --end-hour 17 \
  --summary "Planning Session" \
  --description "Q2 roadmap discussion" \
  --location "Conference Room" \
  --attendees "alice@example.com,bob@example.com"
```

**Parameters**: All optional with defaults.  
Required date/time params if not using defaults: `--year`, `--month`, `--day`, `--start-hour`, `--end-hour`.  
Optional: `--timezone` (default: America/Santiago), `--summary`, `--description`, `--location`, `--attendees`.

**Returns**: Event link and ID on success.

**Notes**:
- Times converted from specified timezone to UTC automatically
- pytz library required (`pip install pytz`)
- Handles DST automatically

**See**: `skills/create-calendar-event/SKILL.md` | `docs/create_calendar_event.md`

## Configuration

### Email Sender Name & Signature

Edit `libs/google_operations.py`:

```python
SENDER_NAME = "Augustus Machine"  # Appears in From header
SIGNATURE_HTML_FILE = "resources/signature.html"  # Path to HTML signature
```

### Scopes

Default scopes in `libs/google_operations.py`:

```python
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/calendar']
```

Adjust if you need more restrictive permissions (note: changing scopes after initial auth requires re-authentication).

## Integration with AI Agents

This framework is designed for OpenCode-style agent systems. To integrate:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from google_operations import (
    get_gmail_service,
    send_email,
    list_unread_emails,
    get_email_content,
    reply_email,
    get_calendar_service,
    create_event
)

# Agent logic here
unread = list_unread_emails(max_results=5)
for email in unread:
    content = get_email_content(email['id'])
    # ... agent reasoning ...
    send_email(to='someone@example.com', subject='Auto reply', body_html='Response')
```

Agents can also load skill specifications from `skills/*/SKILL.md` to discover capabilities dynamically.

## Orchestration Patterns

The `article.md` file documents advanced patterns:

- **Email-to-calendar workflow**: Parse booking requests from emails → create events
- **Intelligent reply agent**: Monitor inbox → analyze → auto-respond with context
- **Parallel branching**: Check multiple calendars → propose meeting times
- **Conditional routing**: Handle failures, retries, escalations
- **Sense-reason-act loops**: Continuous autonomous operation

## Security Considerations

- **Never commit** `credentials/google_credentials.json` or `credentials/google_token.json` to version control. Add `credentials/` to `.gitignore`.
- Protect `google_token.json` - it contains refresh tokens that grant persistent access.
- Use the principle of least privilege: request only necessary OAuth scopes.
- For production deployments, consider service accounts with domain-wide delegation (Google Workspace only).
- Publish your OAuth app (Google Cloud Console) to avoid 7-day token expiry for autonomous agents.
- Rotate credentials periodically and audit token usage.

## Troubleshooting

**"Failed to authenticate" or token errors:**
- Delete `credentials/google_token.json` and re-run `quickstart_google_suite.py`
- Ensure `credentials/google_credentials.json` is correct and matches the OAuth client ID
- Verify test users are added to OAuth consent screen (if app not published)

**Port 8080 already in use during auth:**
- The scripts use `port=0` to auto-select, but `quickstart_google_suite.py` uses 8080. Kill the process on that port or edit the script to use `port=0`.

**"invalid_grant" errors:**
- Refresh token expired (7-day limit for unpublished apps) → re-authenticate
- OAuth client type mismatch → ensure you created "Desktop app" credentials
- Clock skew → sync system time

**API not enabled errors:**
- Verify both Gmail API and Google Calendar API are enabled in Google Cloud Console

**HTML signature not appearing:**
- Check `SIGNATURE_HTML_FILE` path in `libs/google_operations.py`
- Ensure file exists and is readable

**Missing dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz
```

## Dependencies

- Python 3.8+
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`
- `pytz` (calendar only)

Install all:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz
```

## Documentation

- **Comprehensive Tutorial**: `article.md` - Setup guide, architecture deep-dive, orchestration patterns, OAuth 2.0 explanation
- **Skill Specifications**: `skills/*/SKILL.md` - Machine-readable skill definitions
- **Detailed References**: `docs/*.md` - Parameter dictionaries, error handling, advanced examples
- **OpenCode Tool Usage**: See `skills/opencode-tool-usage/SKILL.md` for integrating these skills into agent systems

## License

MIT (see individual files for specifics)

## Credits

Developed by **Augustus Machine** (autonomous agent) working along **Carlos Baeza Negroni**.  
This framework embodies the "openclaw" vision: systems that can autonomously manipulate digital tools to accomplish meaningful work.

- Carlos Baeza Negroni LinkedIn: https://www.linkedin.com/in/carlos-baeza-negroni
- GitHub: https://github.com/cjbaezilla

---

**For questions, issues, or contributions**, refer to the repository's issue tracker or consult the extensive documentation in `article.md`.
