import asyncio
import os
import io
import subprocess
import time
from datetime import datetime, timedelta
from TikTokLive import TikTokLiveClient
import whisper_timestamped as whisper
from docx import Document
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

# Constants
USERNAME = "Official_Allmoney_04"  # Without @
KEYWORDS = ["wally", "callwally", "six"]  # Lowercase
MAIN_FOLDER_ID = "your_main_folder_id_here"  # Replace with actual ID
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "service.json"
POLL_INTERVAL = 30  # Seconds
WHISPER_MODEL = "base"  # Or "large" for better accuracy

# Initialize Google Drive service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# Helper: Get or create date folder
def get_or_create_folder(date_str):
    query = f"name='{date_str}' and mimeType='application/vnd.google-apps.folder' and '{MAIN_FOLDER_ID}' in parents and trashed=false"
    results = drive_service.files().list(q=query).execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]["id"]
    else:
        folder_metadata = {
            "name": date_str,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [MAIN_FOLDER_ID],
        }
        folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
        return folder.get("id")

# Helper: Get current counter from Drive
def get_counter():
    query = f"name='counter.txt' and '{MAIN_FOLDER_ID}' in parents and trashed=false"
    results = drive_service.files().list(q=query).execute()
    files = results.get("files", [])
    if files:
        file_id = files[0]["id"]
        content = drive_service.files().get_media(fileId=file_id).execute().decode("utf-8")
        return int(content.strip())
    return 0

# Helper: Update counter in Drive
def update_counter(new_counter, file_id=None):
    metadata = {"name": "counter.txt", "parents": [MAIN_FOLDER_ID]}
    media = MediaIoBaseUpload(io.BytesIO(str(new_counter).encode()), mimetype="text/plain")
    if file_id:
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    else:
        drive_service.files().create(body=metadata, media_body=media).execute()

# Helper: Upload file to Drive
def upload_file(file_path, file_name, folder_id, mime_type):
    metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type)
    drive_service.files().create(body=metadata, media_body=media, fields="id").execute()
    print(f"Uploaded {file_name}")

# Main loop
counter = get_counter()
model = whisper.load_model(WHISPER_MODEL)  # Load once
counter_file_id = None  # Will set if exists
query = f"name='counter.txt' and '{MAIN_FOLDER_ID}' in parents"
results = drive_service.files().list(q=query).execute()
if results.get("files"):
    counter_file_id = results["files"][0]["id"]

while True:
    print(f"Checking if {USERNAME} is live...")
    is_live = asyncio.run(TikTokLiveClient(unique_id=f"@{USERNAME}").is_live())
    if is_live:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        counter += 1
        video_name = f"{counter}-Official_Allmoney_04-{date_str}-{time_str}-video.mp4"
        trans_name = f"{counter}-Official_Allmoney_04-{date_str}-{time_str}-transcription.docx"
        excel_name = f"{counter}-Official_Allmoney_04-{date_str}-{time_str}-keywords.xlsx"
        print(f"Live detected! Recording to {video_name}")

        # Record with Streamlink (blocks until live ends)
        live_url = f"https://www.tiktok.com/@{USERNAME}/live"
        subprocess.call(["streamlink", "--output", video_name, live_url, "best"])

        # Transcribe
        print("Transcribing...")
        audio = whisper.load_audio(video_name)
        result = whisper.transcribe(model, audio, language="en")  # Assume English; adjust if needed

        # Save .docx
        doc = Document()
        doc.add_paragraph(result["text"])
        doc.save(trans_name)

        # Keyword analysis
        occurrences = []
        for seg in result["segments"]:
            for word_data in seg["words"]:
                word = word_data["word"].strip().lower()
                if word in KEYWORDS:
                    sentence = seg["text"]
                    vid_ts = word_data["start"]
                    abs_time = now + timedelta(seconds=vid_ts)
                    occurrences.append({
                        "keyword": word,
                        "sentence": sentence,
                        "date_time": abs_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "video_timestamp": vid_ts,
                    })

        if occurrences:
            df = pd.DataFrame(occurrences)
            df["count"] = df.groupby("keyword")["keyword"].transform("count")
            df = df[["keyword", "sentence", "date_time", "count", "video_timestamp"]]
            df.to_excel(excel_name, index=False)
        else:
            # Empty excel if no keywords
            pd.DataFrame(columns=["keyword", "sentence", "date_time", "count", "video_timestamp"]).to_excel(excel_name, index=False)

        # Upload
        folder_id = get_or_create_folder(date_str)
        upload_file(video_name, video_name, folder_id, "video/mp4")
        upload_file(trans_name, trans_name, folder_id, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        upload_file(excel_name, excel_name, folder_id, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Clean up local files
        os.remove(video_name)
        os.remove(trans_name)
        os.remove(excel_name)

        # Update counter
        update_counter(counter, counter_file_id)

        print("Processing complete.")
    else:
        print("Not live. Sleeping...")
    time.sleep(POLL_INTERVAL)
