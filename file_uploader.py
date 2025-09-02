from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_or_create_folder(service, folder_name, parent_id=None):
    """Finds or creates a folder by name under an optional parent folder."""
    print(f"🔍 Searching for folder '{folder_name}' in parent '{parent_id}'...")
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    response = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    folders = response.get('files', [])

    if folders:
        print(f"✅ Found folder '{folder_name}' with ID: {folders[0]['id']}")
        return folders[0]['id']
    
    print(f"📁 Creating folder '{folder_name}'...")
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]

    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f"✅ Folder '{folder_name}' created with ID: {folder['id']}")
    return folder['id']

def upload_to_gdrive(mp3_file_path, uploading_folder):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # Step 1: Get or create folders
    root_folder_id = get_or_create_folder(service, 'Translatar_AI')
    user_audio_folder_id = get_or_create_folder(service, uploading_folder, parent_id=root_folder_id)

    # Step 2: Upload the file
    file_metadata = {
        'name': os.path.basename(mp3_file_path),
        'parents': [user_audio_folder_id]
    }
    media = MediaFileUpload(mp3_file_path, mimetype='audio/mpeg')

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')

    # Step 3: Make file public
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    file_url = f"https://drive.google.com/file/d/{file_id}/view"
    return file_url

# # 🔁 Run the upload
# upload_to_gdrive('ai_text_audio_2025-05-27_13-11-32.wav','bot_audio')  # Replace with your actual file path