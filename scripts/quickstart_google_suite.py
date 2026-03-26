import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Full access for agents (read, send, modify, delete, labels, etc.)
# If you want more limited access, change this later and delete token.json
SCOPES = ['https://mail.google.com/']

def main():
    creds = None
    # token.json stores the refresh token (this is what your agent needs)
    if os.path.exists('credentials/token.json'):
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials/google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080, verify=False)   # Disable SSL verification

        # Save the tokens (including refresh token)
        with open('credentials/token.json', 'w') as token:
            token.write(creds.to_json())

    print("[SUCCESS] token.json created with your refresh token.")
    print("Your agent can now use this file forever.")

if __name__ == '__main__':
    main()