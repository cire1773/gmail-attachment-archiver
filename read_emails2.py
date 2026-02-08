import os
import io
import base64
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the required scopes (Combined Drive and Gmail)
SCOPES = [
    'https://www.googleapis.com/auth/drive.file', 
    'https://www.googleapis.com/auth/gmail.readonly'
]

def get_credentials():
    """
    Authenticate and return valid user credentials.
    Handles the OAuth 2.0 flow for both Gmail and Drive scopes.
    """
    creds = None
    token_file = os.getenv('GMAIL_CREDENTIALS_PATH')
    client_secret_file = os.getenv('CLIENT_SECRET_PATH')

    # Check if token file exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If no valid credentials, perform the OAuth 2.0 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("Fetching new tokens via OAuth flow...")
            if not client_secret_file or not os.path.exists(client_secret_file):
                raise FileNotFoundError(f"Client secret file not found at: {client_secret_file}")
                
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return creds

def create_drive_folder(service):
    """Create a new folder in Google Drive with the current date."""
    # Get current date (Note: This is the run date, per your preference)
    folder_name = datetime.datetime.now().strftime("%m-%Y")

    # Define the folder metadata
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Create the folder in Google Drive
    # Note: This does not check if the folder already exists, so it may create duplicates.
    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"Created folder '{folder_name}' in Google Drive with ID: {folder.get('id')}")
    return folder.get('id')

def file_exists_in_drive(service, file_name, folder_id):
    """Check if a file with the same name already exists in the specified Google Drive folder."""
    # Escaping single quotes in file_name is a good practice for Drive queries
    safe_name = file_name.replace("'", "\\'")
    query = f"'{folder_id}' in parents and name = '{safe_name}' and trashed = false"
    
    response = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    files = response.get('files', [])
    return len(files) > 0

def upload_to_drive(service, file_name, file_data, folder_id):
    """Upload a file to Google Drive."""
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    # Create a media object from the file data
    media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype='application/octet-stream')

    # Upload the file
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_name} to Google Drive with ID: {file.get('id')}")

def download_attachments(gmail_service, drive_service, query, drive_folder_id):
    """
    Download email attachments matching allowed extensions and upload them to Google Drive.
    """
    # Parse allowed extensions from .env
    extensions_env = os.getenv('ALLOWED_EXTENSIONS', '')
    # Create a list of allowed extensions, e.g., ['.pdf', '.jpg']
    allowed_extensions = [ext.strip().lower() for ext in extensions_env.split(',') if ext.strip()]

    print(f"Searching for messages with query: {query}")
    results = gmail_service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return

    print(f"Found {len(messages)} messages. Processing...")

    for msg in messages:
        msg_id = msg['id']
        message = gmail_service.users().messages().get(userId='me', id=msg_id).execute()

        # Check if the message has any payload and parts
        if 'payload' in message and 'parts' in message['payload']:
            for part in message['payload']['parts']:
                filename = part.get('filename')
                
                # Check if it has a filename and an attachment ID
                if filename and 'attachmentId' in part['body']:
                    # CHECK: Is this file extension allowed?
                    # We check if the filename ends with any of the allowed extensions
                    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
                        # print(f"Skipping {filename} (extension not allowed)") # Uncomment for debug
                        continue

                    # CHECK: Does file exist in Drive?
                    if file_exists_in_drive(drive_service, filename, drive_folder_id):
                        print(f"File '{filename}' already exists in Drive folder, skipping.")
                        continue

                    # Download the attachment
                    attachment_id = part['body']['attachmentId']
                    attachment = gmail_service.users().messages().attachments().get(
                        userId='me', messageId=msg_id, id=attachment_id
                    ).execute()

                    file_data = base64.urlsafe_b64decode(attachment['data'])

                    # Upload to Drive
                    upload_to_drive(drive_service, filename, file_data, drive_folder_id)
                    print(f"Success: {filename}")
        else:
            # Note: This prints for simple text emails too, which is expected behavior
            pass

def main():
    """Main function to run the script."""
    try:
        # 1. Authenticate once
        creds = get_credentials()
        
        # 2. Build both services using the same credentials
        drive_service = build('drive', 'v3', credentials=creds)
        gmail_service = build('gmail', 'v1', credentials=creds)

        # 3. Create the destination folder
        drive_folder_id = create_drive_folder(drive_service)

        # 4. Get query from env and print error if the query doesn't exist
        query = os.getenv('GMAIL_SEARCH_QUERY')
        if not query:
            print("Error: GMAIL_SEARCH_QUERY not found in .env file.")
            return

        # 5. Run the main logic
        download_attachments(gmail_service, drive_service, query, drive_folder_id)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()