#!/usr/bin/env python3
"""
Tool to reply to an email using Gmail.
This is an OpenCode custom tool that calls google_operations.reply_email.
"""

import sys
import os
import argparse

# Add libs directory to path to import google_operations
# Script is in scripts/google/, libs is in libs/
libs_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))
if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)

def main():
    parser = argparse.ArgumentParser(description='Reply to an email using Gmail')
    parser.add_argument('--message-id', required=True, help='Gmail message ID of the email to reply to')
    parser.add_argument('--body', required=True, help='Email reply body content (will be sent as HTML only)')
    parser.add_argument('--body-file', help='Path to file containing email reply body (will be sent as HTML only)')
    parser.add_argument('--cc', help='CC recipient email address(es), comma-separated')

    args = parser.parse_args()

    if not args.body and not args.body_file:
        parser.error('Either --body or --body-file is required')

    if args.body and args.body_file:
        parser.error('--body and --body-file cannot be used together')

    try:
        from google_operations import reply_email
    except ImportError as e:
        print(f"Error: Could not import google_operations: {e}")
        sys.exit(1)

    # Determine body text from either argument or file
    if args.body_file:
        try:
            with open(args.body_file, 'r', encoding='utf-8') as f:
                body_text = f.read()
        except IOError as e:
            print(f"Error reading body file: {e}")
            sys.exit(1)
    else:
        body_text = args.body

    # Send the reply
    email_id = reply_email(
        message_id=args.message_id,
        body_html=body_text,
        cc=args.cc
    )

    if email_id:
        print(f"Reply sent successfully! ID: {email_id}")
        sys.exit(0)
    else:
        print("Failed to send reply")
        sys.exit(1)

if __name__ == "__main__":
    main()