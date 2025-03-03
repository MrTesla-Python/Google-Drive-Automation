import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_folder(service, name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get('files', [])

def copy_file(service, file_id, new_title, parent_id):
    copied_file_metadata = {
        'name': new_title,
        'parents': [parent_id],
    }
    copied_file = service.files().copy(fileId=file_id, body=copied_file_metadata).execute()
    return copied_file.get('id')

def copy_folder(service, source_folder_id, parent_id=None):
    # Get the name of the source folder
    source_folder = service.files().get(fileId=source_folder_id, fields='name').execute()
    folder_name = source_folder.get('name')

    # Create a new folder with the same name in the destination parent folder
    new_folder_id = create_folder(service, folder_name, parent_id)

    # List all files in the source folder
    files = list_files_in_folder(service, source_folder_id)
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            # If the file is a folder, copy it recursively
            copy_folder(service, file['id'], new_folder_id)
        else:
            # If the file is not a folder, copy it
            copy_file(service, file['id'], file['name'], new_folder_id)
    return new_folder_id

if __name__ == '__main__':
    source_folder_id = '1TDxsCkXSOZPDzvB1JUEIG8IdNlP-LtYb'  # ID of the source folder
    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)

    # Copy the entire folder structure recursively
    new_folder_id = copy_folder(drive_service, source_folder_id)

    print(f"Files copied to new folder with ID: {new_folder_id}")
