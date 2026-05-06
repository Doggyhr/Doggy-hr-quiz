import os, json, io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

creds_info = json.loads(os.environ['GDRIVE_CREDENTIALS'])
creds = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)
service = build('drive', 'v3', credentials=creds)

results = service.files().list(
    q="name='Doggy HR \u2014 Ready to Deploy' and mimeType='application/vnd.google-apps.folder' and trashed=false",
    fields="files(id, name)"
).execute()
folders = results.get('files', [])
if not folders:
    print("ERROR: Deploy folder not found")
    exit(1)

folder_id = folders[0]['id']
print(f"Found folder: {folder_id}")

results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name, mimeType)"
).execute()
files = results.get('files', [])
if not files:
    print("ERROR: No files in deploy folder")
    exit(1)

for file in files:
    print(f"Downloading: {file['name']}")
    request = service.files().get_media(fileId=file['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    with open(file['name'], 'wb') as f:
        f.write(fh.getvalue())
    print(f"Saved: {file['name']}")

print("All files downloaded")
