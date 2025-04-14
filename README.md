📄 open_on_gsuite

A small Windows utility that lets you open .docx, .xlsx, and .pptx files directly in Google Docs, Sheets, or Slides — using the "Open with > Choose another app > Always use this app" feature in Windows.

Instead of launching Microsoft Office or another local editor, this app uploads the file to your Google Drive and opens it instantly in the corresponding Google Workspace app in your browser.
✨ Features

    Open .docx, .xlsx, and .pptx files in Google Docs, Sheets, or Slides

    Runs as a default app for Office files via Windows "Open with"

    Securely authenticates using your own Google account

    Uploads and opens documents automatically after first-time setup

    Stores tokens and configs safely in the user's AppData folder

🔐 Why your own client_secret.json?

This app uses the Google Drive API and OAuth 2.0. Since this is a personal tool, each user must create their own Google API credentials. Your data stays private — nothing is shared with anyone.

🚀 Getting Started

1. Create your Google API credentials

    Go to the Google Cloud Console

    Create a new project (or use an existing one)

    Enable the Google Drive API

    Go to APIs & Services > Credentials

    Click Create Credentials > OAuth Client ID

    Choose Desktop App

    Download the client_secret.json file

2. Run the app

    On first run, it will ask you to select your client_secret.json file

    You'll be redirected to a Google login page — sign in and allow access

    From now on, double-clicking an Office file will open it in Google Workspace

📁 File Storage

    client_secret.json is only used once during initial setup

    OAuth tokens and config are stored securely in:

    C:\Users\YourUsername\AppData\Local\open_on_gsuite\

🔒 Privacy Notice

This app does not collect or transmit any user data. All authentication and file handling is performed securely between your machine and Google.

🛠 Build Info

    Built with Python and PyInstaller

    Static assets (e.g., app icon) are located in the static/ folder

    PyInstaller spec file is included for reproducible builds
