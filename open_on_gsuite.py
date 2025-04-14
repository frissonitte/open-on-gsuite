import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SAVED_FOLDER = os.path.expanduser(r"~\AppData\Local\open-on-gsuite")

if not os.path.exists(SAVED_FOLDER):
    os.makedirs(SAVED_FOLDER)

CONFIG_FILE = os.path.join(SAVED_FOLDER, "config.json")
TOKEN_FILE = os.path.join(SAVED_FOLDER, "token.json")


def select_client_secret():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Please select your client_secret.json file.",
        filetypes=[("JSON files", "*.json")],
    )
    return file_path if file_path else None


def get_client_secret_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            if "client_secret" in config and os.path.exists(config["client_secret"]):
                return config["client_secret"]

    path = select_client_secret()
    if path:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"client_secret": path}, f)
        return path
    return None


SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_SECRET_FILE = get_client_secret_path()
if CLIENT_SECRET_FILE is None:
    print("client_secret.json not selected. Exiting.")
    sys.exit(1)
PARENT_FOLDER_ID = None


def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def find_existing_file(service, file_name, file_md5=None):
    query = f"name='{file_name}' and trashed=false"
    if PARENT_FOLDER_ID:
        query += f" and '{PARENT_FOLDER_ID}' in parents"

    try:
        results = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name, mimeType, md5Checksum, webViewLink)",
                pageSize=10,
            )
            .execute()
        )
        files = results.get("files", [])

        for f in files:
            if (
                file_md5
                and f.get("md5Checksum")
                and f["md5Checksum"].lower() == file_md5.lower()
            ):
                return [f]
            elif not file_md5:
                return [f]
        return []
    except Exception as e:
        print(f"Warning: Error searching for existing file - {str(e)}")
        return []


def upload_or_open(service, file_path):
    file_name = os.path.basename(file_path)

    try:
        file_md5 = calculate_md5(file_path)
    except Exception as e:
        print(f"Warning: Could not calculate file hash - {str(e)}")
        file_md5 = None

    if file_md5:
        existing_files = find_existing_file(service, file_name, file_md5)
        if existing_files:
            print(f"Opening existing file: {existing_files[0]['webViewLink']}")
            return existing_files[0]["webViewLink"]

    try:
        existing_files = find_existing_file(service, file_name, None)
        if existing_files:
            print(f"Opening possible matching file: {existing_files[0]['webViewLink']}")
            print("Note: Content verification was not possible")
            return existing_files[0]["webViewLink"]
    except Exception as e:
        print(f"Warning: Error searching for files - {str(e)}")

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:

        ext = os.path.splitext(file_path)[1].lower()
        fallback_map = {
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".pdf": "application/pdf",
        }
        mime_type = fallback_map.get(ext)

    if not mime_type:
        raise ValueError("Could not determine MIME type of the file.")

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file_metadata = {
        "name": file_name,
        "parents": [PARENT_FOLDER_ID] if PARENT_FOLDER_ID else None,
    }

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="webViewLink")
        .execute()
    )

    print(f"Uploaded new file: {file['webViewLink']}")
    return file["webViewLink"]


def main():
    if len(sys.argv) != 2:
        print("Usage: python drive_upload.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        sys.exit(1)

    try:
        service = build("drive", "v3", credentials=authenticate())
        url = upload_or_open(service, file_path)

        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        user_data_dir = os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data")
        profile_dir = "Profile 2"

        subprocess.Popen(
            [
                edge_path,
                f"--user-data-dir={user_data_dir}",
                f"--profile-directory={profile_dir}",
                url,
            ]
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
