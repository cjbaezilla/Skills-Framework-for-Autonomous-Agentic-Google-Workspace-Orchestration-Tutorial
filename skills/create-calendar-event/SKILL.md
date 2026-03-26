---
name: create-calendar-event
description: Creates Google Calendar events with customizable date, time, timezone, and attendee parameters
license: MIT
compatibility: opencode
metadata:
  tool: create_calendar_event
  category: google-workspace
  audience: developers, productivity-users
---

## What I do
I create Google Calendar events with flexible parameters including:
- Date and time configuration with timezone support
- Event details (title, description, location)
- Attendee management (comma-separated email list)
- Automatic UTC conversion and DST handling
- Integration with Google Calendar API via google_operations.create_event()

## When to use me
Use me when you need to:
- Schedule meetings and appointments programmatically
- Create calendar events from command line or scripts
- Block time for focused work sessions
- Set up recurring events (via additional parameters)
- Add attendees to events automatically

## How to invoke me
```
python scripts/google/create_calendar_event.py --year 2026 --month 3 --day 26 --start-hour 15 --end-hour 17 --summary "coordination meeting" --description "Weekly sync" --attendees "alice@example.com,bob@example.com"
```

## Parameters
All parameters are optional with sensible defaults:
- `--year`: Event year (default: 2026)
- `--month`: Event month 1-12 (default: 3)
- `--day`: Event day 1-31 (default: 28)
- `--start-hour`: Start hour in 24h format 0-23 (default: 17)
- `--end-hour`: End hour in 24h format 0-23 (default: 19)
- `--timezone`: Timezone identifier (default: America/Santiago)
- `--summary`: Event title/description (default: "Calendar Event")
- `--description`: Event description details
- `--location`: Event location
- `--attendees`: Comma-separated list of attendee email addresses

## Return values
On success:
- Event link (htmlLink)
- Event ID

On failure:
- Error message with reason

## Example usage
```bash
# Create a simple 2-hour meeting
python scripts/google/create_calendar_event.py --year 2025 --month 3 --day 30 --start-hour 14 --end-hour 16 --summary "Project Kickoff" --location "Conference Room A"

# Create meeting with multiple attendees
python scripts/google/create_calendar_event.py --summary "Team Standup" --start-hour 9 --end-hour 9 --attendees "team@example.com,product@example.com" --description "Daily sync"

# All-day event (set start and end to same day, 0-24)
python scripts/google/create_calendar_event.py --day 25 --month 12 --start-hour 0 --end-hour 23 --summary "Company Holiday" --description "Office closed for Christmas"
```

## Notes
- Requires `pytz` library (install with: pip install pytz)
- Requires Google Calendar API authentication via google_operations library
- Times automatically convert from specified timezone to UTC
- Supports DST (Daylight Saving Time) automatically through pytz
- For more advanced features (recurrence, reminders, colors, etc.), extend the script or use the google_operations library directly

## Further Documentation
For comprehensive API parameter reference, examples, and advanced features, see:
`docs/create_calendar_event.md`
