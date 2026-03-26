import os.path
import base64
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Full access (matches what you chose in quickstart)
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/calendar']

# ========== CONFIGURATION ==========
SENDER_NAME = "Augustus Machine"  # Your display name (will appear as: "Name <email@gmail.com>")
# HTML signature file (required for signatures)
SIGNATURE_HTML_FILE = "resources/signature.html"  # HTML signature
# ===================================

# Global cache for user email
_cached_user_email = None

def get_user_email(service):
    """Get authenticated user's email address from Gmail profile (cached)"""
    global _cached_user_email
    if _cached_user_email is None:
        try:
            profile = service.users().getProfile(userId='me').execute()
            _cached_user_email = profile.get('emailAddress', '')
        except Exception as e:
            print(f"Warning: Could not get user email from profile: {e}")
            _cached_user_email = ""
    return _cached_user_email

def load_signature():
    """Load HTML signature from configured file
    
    Returns:
        str: HTML signature content
    """
    with open(SIGNATURE_HTML_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_gmail_service():
    """Returns the Gmail service ready to use. Auto-refreshes token if needed."""
    creds = None
    if os.path.exists('credentials/google_token.json'):
        creds = Credentials.from_authorized_user_file('credentials/google_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh credentials: {e}")
                creds = None
        if not creds:
            # This should never run again unless you delete token.json
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file('credentials/google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Failed to authenticate: {e}")
                return None
        # Save refreshed token
        with open('credentials/google_token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build Gmail service: {e}")
        return None

def get_calendar_service():
    """Returns the Calendar service ready to use. Auto-refreshes token if needed."""
    creds = None
    if os.path.exists('credentials/google_token.json'):
        creds = Credentials.from_authorized_user_file('credentials/google_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh credentials: {e}")
                creds = None
        if not creds:
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file('credentials/google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Failed to authenticate: {e}")
                return None
        # Save refreshed token
        with open('credentials/google_token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build Calendar service: {e}")
        return None

# ====================== AGENTIC FUNCTIONS ======================

def list_unread_emails(max_results=10):
    """Returns list of unread emails (subject, sender, snippet, id)"""
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = msg_data['payload']['headers']
        subject = next(h['value'] for h in headers if h['name'] == 'Subject')
        sender = next(h['value'] for h in headers if h['name'] == 'From')
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'from': sender,
            'snippet': msg_data.get('snippet', '')
        })
    return emails

def search_emails(query="from:someone@example.com", max_results=5):
    """Search Gmail with any Gmail query syntax (e.g. 'subject:invoice', 'after:2025-03-01')"""
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    return [msg['id'] for msg in messages]

def get_email_content(message_id):
    """Get full email: subject, from, body (plain text)"""
    service = get_gmail_service()
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    
    # Get plain text body
    parts = msg['payload'].get('parts', [msg['payload']])
    body = ""
    for part in parts:
        if part.get('mimeType') == 'text/plain':
            data = part['body'].get('data', '')
            body = base64.urlsafe_b64decode(data).decode('utf-8')
            break
    
    return {
        'id': message_id,
        'subject': subject,
        'from': sender,
        'body': body[:2000] + "..." if len(body) > 2000 else body  # truncate for safety
    }

def send_email(to, subject, body_html, cc=None):
    """Send an email as HTML only (no plain text alternative) with HTML signature
    
    Args:
        to: Recipient email address
        subject: Email subject
        body_html: Email body content in plain text (will be converted to HTML)
        cc: CC recipient(s), comma-separated string or None
    
    Note: This function always sends HTML-only messages. The body_html parameter
    accepts plain text which is automatically converted to HTML with proper escaping.
    All newlines are converted to proper HTML paragraph and line break tags.
    """
    service = get_gmail_service()
    if not service:
        print("[ERROR] Cannot send email: Gmail service not available")
        return None

    # Load HTML signature (always included)
    html_sig = load_signature()
    
    # Create HTML-only message
    message = MIMEText('', 'html', 'utf-8')
    
    # Prepare HTML body
    html_body = ""
    if body_html:
        # Escape HTML special chars
        escaped_body = body_html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Normalize line endings: convert \r\n and \r to \n
        normalized = escaped_body.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into paragraphs (separated by blank lines)
        paragraphs = []
        current_para = []
        for line in normalized.split('\n'):
            stripped = line.rstrip('\n')
            if stripped:  # Non-empty line
                current_para.append(stripped)
            else:  # Empty line - paragraph separator
                if current_para:
                    paragraphs.append('<p>' + '<br />\n'.join(current_para) + '</p>')
                    current_para = []
        
        # Add the last paragraph if any
        if current_para:
            paragraphs.append('<p>' + '<br />\n'.join(current_para) + '</p>')
        
        # If no paragraphs (empty/whitespace only), create empty paragraph
        if not paragraphs:
            paragraphs = ['<p></p>']
        
        html_body = '\n'.join(paragraphs)
        html_body = f'<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">{html_body}</div>'
    
    # Add HTML signature
    html_body = (html_body + '\n' if html_body else '') + html_sig
    
    if html_body:
        message.set_payload(html_body, 'utf-8')
    else:
        message.set_payload('', 'utf-8')
    
    # Set required headers
    message['to'] = to
    message['subject'] = subject

    # Add CC header if provided
    if cc:
        message['cc'] = cc

    # Set From header with sender name if configured
    if SENDER_NAME:
        user_email = get_user_email(service)
        if user_email:
            message['from'] = f"{SENDER_NAME} <{user_email}>"
        else:
            # Fallback: just the name (Gmail may still add email)
            message['from'] = SENDER_NAME

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        sent = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        print(f"[OK] Email sent! ID: {sent['id']}")
        return sent['id']
    except HttpError as error:
        print(f"[ERROR] HTTP error sending email: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Unexpected error sending email: {type(error).__name__}: {error}")
        return None

def reply_email(message_id, body_html, cc=None):
    """Reply to an existing email thread using Gmail API

    Args:
        message_id: Gmail message ID of the original email to reply to
        body_html: Email reply body content in plain text (will be converted to HTML)
        cc: CC recipient(s), comma-separated string or None

    Note: This function sends HTML-only messages and automatically sets
    In-Reply-To and References headers to maintain email threading.
    """
    service = get_gmail_service()
    if not service:
        print("[ERROR] Cannot reply to email: Gmail service not available")
        return None

    # Load HTML signature (always included)
    html_sig = load_signature()

    # Create HTML-only message
    message = MIMEText('', 'html', 'utf-8')

    # Prepare HTML body (same logic as send_email)
    html_body = ""
    if body_html:
        escaped_body = body_html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        normalized = escaped_body.replace('\r\n', '\n').replace('\r', '\n')
        paragraphs = []
        current_para = []
        for line in normalized.split('\n'):
            stripped = line.rstrip('\n')
            if stripped:
                current_para.append(stripped)
            else:
                if current_para:
                    paragraphs.append('<p>' + '<br />\n'.join(current_para) + '</p>')
                    current_para = []
        if current_para:
            paragraphs.append('<p>' + '<br />\n'.join(current_para) + '</p>')
        if not paragraphs:
            paragraphs = ['<p></p>']
        html_body = '\n'.join(paragraphs)
        html_body = f'<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5;">{html_body}</div>'

    # Add HTML signature
    html_body = (html_body + '\n' if html_body else '') + html_sig

    if html_body:
        message.set_payload(html_body, 'utf-8')
    else:
        message.set_payload('', 'utf-8')

    # Get original message to extract headers for proper reply
    thread_id = None
    try:
        original_msg = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
        original_headers = original_msg['payload']['headers']
        thread_id = original_msg.get('threadId')

        # Extract Subject, From, To, CC, and Message-ID from original
        subject = next((h['value'] for h in original_headers if h['name'] == 'Subject'), '')
        from_header = next((h['value'] for h in original_headers if h['name'] == 'From'), '')
        to_header = next((h['value'] for h in original_headers if h['name'] == 'To'), '')
        original_cc = next((h['value'] for h in original_headers if h['name'] == 'Cc'), '')
        message_id_header = next((h['value'] for h in original_headers if h['name'] == 'Message-ID'), None)

        # For reply, we need to set In-Reply-To and References headers
        if message_id_header:
            message['In-Reply-To'] = message_id_header
            message['References'] = message_id_header

        # Set subject - preserve the original subject for threading
        if subject:
            message['subject'] = subject

        # Set To header to the original sender (the person we're replying to)
        if from_header:
            message['to'] = from_header
        else:
            print(f"[ERROR] Original message has no From header")
            return None

        # Add CC if provided, but also preserve original CC recipients?
        # Typically when replying, you might want to include original CC
        # For simplicity, we'll only use provided CC
        if cc:
            message['cc'] = cc
        # Note: We don't automatically add original_cc to give user control

        # Add Replies-To header to send replies to the original recipient
        # Since we're replying to an email from someone, our reply should go back to them
        # The To header already points to them, so no need for Reply-To

    except HttpError as error:
        print(f"[ERROR] HTTP error getting original message: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Unexpected error processing original message: {type(error).__name__}: {error}")
        return None

    # Set From header with sender name if configured
    if SENDER_NAME:
        user_email = get_user_email(service)
        if user_email:
            message['from'] = f"{SENDER_NAME} <{user_email}>"
        else:
            message['from'] = SENDER_NAME

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        # Use the send method with threadId to maintain threading
        body = {'raw': raw}
        if thread_id:
            body['threadId'] = thread_id

        sent = service.users().messages().send(
            userId='me',
            body=body
        ).execute()
        print(f"[OK] Reply sent! ID: {sent['id']}")
        return sent['id']
    except HttpError as error:
        print(f"[ERROR] HTTP error sending reply: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Unexpected error sending reply: {type(error).__name__}: {error}")
        return None

# ====================== CALENDAR FUNCTIONS ======================

def list_calendars():
    """Returns list of calendars accessible to the user"""
    service = get_calendar_service()
    if not service:
        print("[ERROR] Cannot list calendars: Calendar service not available")
        return []

    try:
        calendar_list = service.calendarList().list().execute()
        calendars = []
        for cal in calendar_list.get('items', []):
            calendars.append({
                'id': cal['id'],
                'summary': cal.get('summary', ''),
                'description': cal.get('description', ''),
                'primary': cal.get('primary', False),
                'access_role': cal.get('accessRole', ''),
                'backgroundColor': cal.get('backgroundColor', '')
            })
        return calendars
    except HttpError as error:
        print(f"[ERROR] HTTP error listing calendars: {error}")
        return []
    except Exception as error:
        print(f"[ERROR] Unexpected error listing calendars: {type(error).__name__}: {error}")
        return []

def list_events(calendar_id='primary', time_min=None, time_max=None, max_results=100, q=None):
    """List events from a calendar with optional time range and search query"""
    service = get_calendar_service()
    if not service:
        print("[ERROR] Cannot list events: Calendar service not available")
        return []

    # Set default time range if not provided
    if time_min is None:
        time_min = datetime.utcnow().isoformat() + 'Z'
    if time_max is None:
        time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            q=q
        ).execute()
        return events_result.get('items', [])
    except HttpError as error:
        print(f"[ERROR] HTTP error listing events: {error}")
        return []
    except Exception as error:
        print(f"[ERROR] Unexpected error listing events: {type(error).__name__}: {error}")
        return []

def get_event(calendar_id, event_id):
    """Get a specific event by ID"""
    service = get_calendar_service()
    if not service:
        print("[ERROR] Cannot get event: Calendar service not available")
        return None

    try:
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        return event
    except HttpError as error:
        print(f"[ERROR] HTTP error getting event: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Unexpected error getting event: {type(error).__name__}: {error}")
        return None

def create_event(calendar_id='primary', summary=None, start_time=None, end_time=None,
                 description=None, location=None, attendees=None, **kwargs):
    """Create a new calendar event

    Args:
        calendar_id: Calendar ID (default: 'primary')
        summary: Event title
        start_time: datetime object or ISO format string
        end_time: datetime object or ISO format string
        description: Event description
        location: Event location
        attendees: List of email addresses
        **kwargs: Additional event properties (recurrence, reminders, etc.)
    """
    service = get_calendar_service()
    if not service:
        print("[ERROR] Cannot create event: Calendar service not available")
        return None

    # Convert datetime objects to ISO format if needed
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    event = {
        'summary': summary,
        'description': description,
        'location': location,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
    }

    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]

    # Add any additional properties
    event.update(kwargs)

    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"[OK] Event created! ID: {created_event.get('id')}")
        return created_event
    except HttpError as error:
        print(f"[ERROR] HTTP error creating event: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Unexpected error creating event: {type(error).__name__}: {error}")
        return None

def update_event(calendar_id, event_id, **updates):
    """Update an existing event with new properties

    Args:
        calendar_id: Calendar ID
        event_id: Event ID to update
        **updates: Event properties to update (summary, description, start, end, etc.)
    """
    service = get_calendar_service()
    if not service:
        print("[ERROR] Cannot update event: Calendar service not available")
        return None

    # First get the existing event
    try:
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    except HttpError as error:
        if error.resp.status == 404:
            print(f"[ERROR] Event not found: {event_id}")
            return None
        raise

    # Apply updates
    for key, value in updates.items():
        if key in ['start', 'end'] and isinstance(value, datetime):
            event[key] = {'dateTime': value.isoformat(), 'timeZone': 'UTC'}
        else:
            event[key] = value

    try:
        updated_event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        print(f"[OK] Event updated! ID: {updated_event.get('id')}")
        return updated_event
    except HttpError as error:
        print(f"[ERROR] HTTP error updating event: {error}")
        return None
    except Exception as error:
        print(f"[ERROR] Unexpected error updating event: {type(error).__name__}: {error}")
        return None

def delete_event(calendar_id, event_id):
    """Delete an event from a calendar"""
    service = get_calendar_service()
    if not service:
        print("[ERROR] Cannot delete event: Calendar service not available")
        return False

    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"[OK] Event deleted! ID: {event_id}")
        return True
    except HttpError as error:
        if error.resp.status == 404:
            print(f"[WARNING] Event not found (may have been already deleted): {event_id}")
            return True
        print(f"[ERROR] HTTP error deleting event: {error}")
        return False
    except Exception as error:
        print(f"[ERROR] Unexpected error deleting event: {type(error).__name__}: {error}")
        return False