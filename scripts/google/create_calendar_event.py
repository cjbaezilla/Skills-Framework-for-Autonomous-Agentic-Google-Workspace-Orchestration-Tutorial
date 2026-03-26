#!/usr/bin/env python3
"""
Tool to create a Google Calendar event with customizable parameters.
This is an OpenCode custom tool that calls google_operations.create_event.
"""

import sys
import os
import argparse
from datetime import datetime

# Add libs directory to path to import google_operations
# Script is in scripts/google/, libs is in libs/
libs_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))
if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)

def main():
    parser = argparse.ArgumentParser(description='Create a Google Calendar event')
    parser.add_argument('--year', type=int, default=2026, help='Event year (default: 2026)')
    parser.add_argument('--month', type=int, default=3, help='Event month (default: 3)')
    parser.add_argument('--day', type=int, default=28, help='Event day (default: 28)')
    parser.add_argument('--start-hour', type=int, default=17, help='Start hour in 24h format (default: 17)')
    parser.add_argument('--end-hour', type=int, default=19, help='End hour in 24h format (default: 19)')
    parser.add_argument('--timezone', default='America/Santiago', help='Timezone (default: America/Santiago)')
    parser.add_argument('--summary', default='Calendar Event', help='Event title (default: Calendar Event)')
    parser.add_argument('--description', default='', help='Event description')
    parser.add_argument('--location', default='', help='Event location')
    parser.add_argument('--attendees', default='', help='Comma-separated list of attendee email addresses')
     
    args = parser.parse_args()

    try:
        import pytz
    except ImportError:
        print("Error: pytz is required. Install with: pip install pytz")
        sys.exit(1)

    from google_operations import create_event

    # Use specified timezone (handles DST automatically)
    tz = pytz.timezone(args.timezone)

    # Create local datetime objects with timezone
    start_local = tz.localize(datetime(args.year, args.month, args.day, args.start_hour, 0, 0))
    end_local = tz.localize(datetime(args.year, args.month, args.day, args.end_hour, 0, 0))

    # Convert to UTC as Google Calendar API expects UTC
    start_utc = start_local.astimezone(pytz.UTC)
    end_utc = end_local.astimezone(pytz.UTC)

    # Process attendees
    attendees = None
    if args.attendees:
        # Split by comma and strip whitespace
        attendees = [email.strip() for email in args.attendees.split(',') if email.strip()]

    # Create the event
    event = create_event(
        summary=args.summary,
        start_time=start_utc,
        end_time=end_utc,
        timeZone=args.timezone,
        description=args.description if args.description else None,
        location=args.location if args.location else None,
        attendees=attendees
    )

    if event:
        print(f"Event created: {event.get('htmlLink')}")
        print(f"Event ID: {event.get('id')}")
        sys.exit(0)
    else:
        print("Failed to create event")
        sys.exit(1)

if __name__ == "__main__":
    main()