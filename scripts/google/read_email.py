#!/usr/bin/env python3
"""
Tool to read emails from Gmail inbox.
This is an OpenCode custom tool that calls google_operations.list_unread_emails and get_email_content.
"""

import sys
import os
import argparse
import json

# Add libs directory to path to import google_operations
# Script is in scripts/google/, libs is in libs/
libs_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))
if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)

def main():
    parser = argparse.ArgumentParser(description='Read emails from Gmail inbox')
    parser.add_argument('--list', action='store_true', help='List unread emails (default action)')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of emails to list (default: 10)')
    parser.add_argument('--message-id', help='Read specific email by message ID')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    
    args = parser.parse_args()

    # Default to list if no specific action
    if not args.message_id and not args.list:
        args.list = True

    try:
        from google_operations import list_unread_emails, get_email_content
    except ImportError as e:
        print(f"Error: Could not import google_operations: {e}", file=sys.stderr)
        sys.exit(1)

    if args.message_id:
        # Read specific email
        email = get_email_content(args.message_id)
        if not email:
            print(f"Error: Could not retrieve email with ID: {args.message_id}", file=sys.stderr)
            sys.exit(1)
        
        if args.format == 'json':
            print(json.dumps(email, indent=2))
        else:
            print(f"ID: {email['id']}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print("\nBody:")
            print(email['body'])
    
    else:
        # List unread emails
        emails = list_unread_emails(max_results=args.max_results)
        
        if args.format == 'json':
            print(json.dumps(emails, indent=2))
        else:
            if not emails:
                print("No unread emails found.")
            else:
                print(f"Found {len(emails)} unread email(s):")
                print("-" * 80)
                for i, email in enumerate(emails, 1):
                    print(f"{i}. ID: {email['id']}")
                    print(f"   From: {email['from']}")
                    print(f"   Subject: {email['subject']}")
                    if email['snippet']:
                        print(f"   Snippet: {email['snippet'][:100]}...")
                    print()

if __name__ == "__main__":
    main()