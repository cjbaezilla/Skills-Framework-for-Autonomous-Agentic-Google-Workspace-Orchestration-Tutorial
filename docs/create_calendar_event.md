# Google Calendar API - Create Event Parameter Reference

## Overview
This document provides a comprehensive reference for all parameters available when creating a calendar event using the Google Calendar API v3 through the `create_event()` function in `gmail_operations.py`.

## Basic Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `calendar_id` | string | Calendar identifier (default: `'primary'`) |
| `summary` | string | Event title/name (required) |
| `start_time` | datetime \| string | Start time as datetime object or ISO 8601 string (required) |
| `end_time` | datetime \| string | End time as datetime object or ISO 8601 string (required) |

## Common Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | string | Event description (supports HTML) |
| `location` | string | Physical or virtual location |
| `attendees` | list<string> | List of attendee email addresses |
| `recurrence` | list<string> | RRULE for recurring events (e.g., `['RRULE:FREQ=DAILY;COUNT=5']`) |
| `reminders` | dict | Notification settings (see Reminders section) |
| `colorId` | string | Event color (1-11) |
| `transparency` | string | `'opaque'` (blocks time, default) or `'transparent'` (doesn't block) |
| `visibility` | string | `'default'`, `'public'`, `'private'`, or `'confidential'` |
| `status` | string | `'confirmed'`, `'tentative'`, or `'cancelled'` |
| `conferenceData` | dict | Video conferencing configuration |

## Event Timing Parameters

### Date/Time Format
Events can be either **specific times** or **all-day** events:

**Specific time:**
```python
start_time={'dateTime': '2025-03-30T14:00:00', 'timeZone': 'America/Los_Angeles'}
end_time={'dateTime': '2025-03-30T15:00:00', 'timeZone': 'America/Los_Angeles'}
```

**All-day event:**
```python
start_time={'date': '2025-03-30'}
end_time={'date': '2025-03-30'}
```

## Recurrence (RRULE Format)

Recurring events use the iCalendar RRULE specification:

### Frequency Options
- `FREQ=DAILY`
- `FREQ=WEEKLY`
- `FREQ=MONTHLY`
- `FREQ=YEARLY`

### Common RRULE Examples

```python
# Daily for 10 occurrences
'RRULE:FREQ=DAILY;COUNT=10'

# Every Monday and Wednesday for 1 month
'RRULE:FREQ=WEEKLY;BYDAY=MO,WE;UNTIL=20250430'

# Every 2 weeks on Friday
'RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=FR'

# Monthly on the 15th
'RRULE:FREQ=MONTHLY;BYMONTHDAY=15'

# Yearly on December 25
'RRULE:FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25'

# Every weekday (Monday-Friday)
'RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR'
```

Multiple recurrence rules can be combined:
```python
recurrence=[
    'RRULE:FREQ=DAILY;COUNT=5',
    'EXDATE:20250327'  # exclusion dates
]
```

## Reminders Configuration

Reminders can be set for the event itself or per-attendee:

```python
reminders={
    'useDefault': False,
    'overrides': [
        {'method': 'email', 'minutes': 60},   # Email 1 hour before
        {'method': 'popup', 'minutes': 15}   # Popup 15 minutes before
    ]
}
```

### Reminder Methods
- `'email'` - Email notification
- `'popup'` - Browser/mobile notification
- `'sms'` - SMS (if available in your region)

### Example Reminder Sets

```python
# Default reminders (use calendar default)
reminders={'useDefault': True}

# Custom multiple reminders
reminders={
    'useDefault': False,
    'overrides': [
        {'method': 'email', 'minutes': 1440},  # 1 day before
        {'method': 'popup', 'minutes': 60},    # 1 hour before
        {'method': 'popup', 'minutes': 10}     # 10 minutes before
    ]
}

# Email only, 24 hours before
reminders={
    'useDefault': False,
    'overrides': [{'method': 'email', 'minutes': 1440}]
}
```

## Color IDs

| colorId | Color Name | Hex Code |
|---------|------------|----------|
| `'1'` | Lavender | `#a4bdfc` |
| `'2'` | Sage | `#7ae7bf` |
| `'3'` | Grape | `#dbadff` |
| `'4'` | Flamingo | `#ff887c` |
| `'5'` | Banana | `#fbd75b` |
| `'6'` | Tangerine | `#ffb878` |
| `'7'` | Peacock | `#46d6b6` |
| `'8'` | Graphite | `#5484ed` |
| `'9'` | Blue | `#51b749` |
| `'10'` | Navy | `#dc2127` |
| `'11'` | Red | `#fff8b1` |

## Transparency

| Value | Description |
|-------|-------------|
| `'opaque'` | Default. Blocks time, shows as busy |
| `'transparent'` | Does not block time, shows as free |

## Visibility

| Value | Description |
|-------|-------------|
| `'default'` | Uses default visibility for the calendar |
| `'public'` | Event is public |
| `'private'` | Event details hidden from others |
| `'confidential'` | Private but shows as busy |

## Conference Data (Google Meet/Zoom)

To add video conferencing:

```python
conferenceData={
    'createRequest': {
        'requestId': 'unique-request-id-123',
        'conferenceSolutionKey': {
            'type': 'hangoutsMeet'  # or 'addOn' for third-party
        }
    }
}
```

**Important:** When using `conferenceData`, you must also:
1. Include `conferenceDataVersion=1` in your API call (handled automatically by the client)
2. Typically, just setting `createRequest` will auto-generate a Meet link

## Guest Permissions

Control what guests can do:

```python
guestsCanInviteOthers=False  # Guests cannot invite others
guestsCanModify=False       # Guests cannot edit event
guestsCanSeeOtherGuests=False  # Guests cannot see other guest list
```

## Extended Properties

Store custom data with your events:

```python
extendedProperties={
    'private': {
        'customField1': 'value1',
        'customField2': 'value2'
    },
    'shared': {
        'team': 'engineering',
        'project': 'api-migration'
    }
}
```

- `private`: Only visible to calendar owner
- `shared`: Visible to all event attendees

## Complete Working Examples

### Basic Meeting with Attendees
```python
from datetime import datetime, timedelta

event = create_event(
    summary='Project Kickoff Meeting',
    start_time=datetime(2025, 3, 30, 14, 0, 0),
    end_time=datetime(2025, 3, 30, 15, 0, 0),
    description='Discuss project goals and timeline',
    location='Conference Room A / Zoom',
    attendees=['alice@example.com', 'bob@example.com'],
    reminders={
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 60},
            {'method': 'popup', 'minutes': 10}
        ]
    },
    guestsCanSeeOtherGuests=True
)
```

### All-Day Event with Color
```python
event = create_event(
    summary='Company Holiday',
    start_time={'date': '2025-12-25'},
    end_time={'date': '2025-12-25'},
    description='Office closed for Christmas',
    colorId='6',  # Tangerine
    visibility='public'
)
```

### Recurring Team Standup with Google Meet
```python
event = create_event(
    summary='Daily Standup',
    start_time=datetime(2025, 3, 31, 9, 0, 0),
    end_time=datetime(2025, 3, 31, 9, 30, 0),
    recurrence=['RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;UNTIL=20250630'],
    description='Daily team sync',
    attendees=['team@example.com'],
    conferenceData={
        'createRequest': {
            'requestId': 'standup-meet-20250330',
            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
        }
    },
    reminders={'useDefault': True}
)
```

### Private All-Day Event (No Details Shown)
```python
event = create_event(
    summary='Busy - Do Not Disturb',
    start_time={'date': '2025-04-15'},
    end_time={'date': '2025-04-15'},
    description='Personal appointment',
    colorId='11',  # Red
    transparency='opaque',
    visibility='private',
    location=''
)
```

## Full Event Object Structure Reference

See the official Google Calendar API v3 reference for complete schema:
https://developers.google.com/calendar/api/v3/reference/events

## Notes

- Times are in UTC by default unless a different timeZone is specified in the start/end objects
- The `create_event()` function accepts any additional event properties via `**kwargs`
- Event IDs are generated automatically upon creation (you can provide `id` in kwargs if needed)
- Maximum event size: 1MB for all data combined
- Maximum attendees: 2000 per event

## See Also

- `list_events()` - Query existing events
- `get_event()` - Retrieve event details
- `update_event()` - Modify existing events
- `delete_event()` - Remove events
- `list_calendars()` - List available calendars

## CLI Usage

$ python create_calendar_event.py --help

usage: create_calendar_event.py [-h] [--year YEAR] [--month MONTH] [--day DAY]
                                [--start-hour START_HOUR] [--end-hour END_HOUR]
                                [--timezone TIMEZONE] [--summary SUMMARY]
                                [--description DESCRIPTION] [--location LOCATION]
                                [--attendees ATTENDEES]

Create a Google Calendar event

options:
  -h, --help            show this help message and exit
  --year YEAR           Event year (default: 2026)
  --month MONTH         Event month (default: 3)
  --day DAY             Event day (default: 28)
  --start-hour START_HOUR
                        Start hour in 24h format (default: 17)
  --end-hour END_HOUR   End hour in 24h format (default: 19)
  --timezone TIMEZONE   Timezone (default: America/Santiago)
  --summary SUMMARY     Event title (default: Calendar Event)
  --description DESCRIPTION
                        Event description
  --location LOCATION   Event location
  --attendees ATTENDEES
                        Comma-separated list of attendee email addresses