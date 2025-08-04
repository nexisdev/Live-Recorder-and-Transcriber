TikTok Live Stream Automator
Overview
This project is an automated Python script designed to monitor TikTok live streams from a specific user (@Official_Allmoney_04), record the streams when they go live, transcribe the audio to text, scan for predefined keywords, and store all outputs (video, transcription, and keyword analysis) in a Google Drive folder. The script runs continuously in a loop, polling for live status and handling the entire workflow end-to-end.
Key features include:
	•	Real-time detection of live streams using the unofficial TikTokLive library.
	•	Video recording via Streamlink.
	•	Audio transcription with timestamps using OpenAI’s Whisper model (via whisper-timestamped).
	•	Keyword detection and reporting in an Excel file.
	•	Automated uploads to Google Drive with organized folder structure.
This setup is ideal for archiving and analyzing live content, such as tracking mentions of specific terms like “Wally”, “CallWally”, or “SiX”.
Features
	•	Live Detection: Polls every 30 seconds to check if the target user is live.
	•	Recording: Captures the live stream as an MP4 file using Streamlink, which automatically stops when the stream ends.
	•	Transcription: Generates a full text transcription in a .docx file with word-level timestamps.
	•	Keyword Analysis: Scans for case-insensitive keywords, logs occurrences with context (sentence, timestamps), and outputs to an .xlsx file.
	•	Storage: Uploads files to Google Drive in date-labeled folders (e.g., “2025-08-04”), with sequential numbering for each recording.
	•	Persistence: Maintains a global counter across runs using a file in Google Drive.
	•	Error Handling: Basic retries and logging for robustness.
Requirements
	•	Python 3.10 or higher.
	•	FFmpeg installed on the system (for audio handling in Streamlink and Whisper).
	•	A Google Cloud service account with Drive API access (for uploads).
	•	Access to a machine/VM where the script can run continuously (e.g., Oracle Cloud Free Tier VM as described in setup guides).
Installation
	1	Clone the Repository (or create files manually): git clone 
	2	cd tiktok-live-automator
	3	
	4	Install System Dependencies:
	◦	On Ubuntu/Linux: sudo apt update
	◦	sudo apt install python3.10 python3-pip ffmpeg -y
	◦	
	◦	On macOS (using Homebrew): brew install python@3.10 ffmpeg
	◦	
	◦	On Windows: Download and install Python from python.org and FFmpeg from ffmpeg.org (add to PATH).
	5	Set Up Virtual Environment (recommended): python3 -m venv venv
	6	source venv/bin/activate  # On Windows: venv\Scripts\activate
	7	
	8	Install Python Dependencies: pip install -r requirements.txt
	9	 Note: The requirements.txt includes CPU-based Torch for Whisper. If you have a GPU, adjust the Torch installation accordingly.
Configuration
	1	Google Drive Setup:
	◦	Create a Google Cloud project at console.cloud.google.com.
	◦	Enable the Google Drive API.
	◦	Create a service account, grant it “Editor” role, and download the JSON key file as service.json.
	◦	Create a main folder in Google Drive (e.g., “TikTokLives”) and note its ID from the URL (e.g., https://drive.google.com/drive/folders/ABC123 → ID = “ABC123”).
	◦	Share the folder with the service account email (found in service.json) with Editor permissions.
	◦	Place service.json in the script’s directory.
	◦	Update MAIN_FOLDER_ID in tiktok_automator.py with your folder ID.
	2	Script Customization (optional):
	◦	Edit tiktok_automator.py:
	▪	Change USERNAME if monitoring a different TikTok user.
	▪	Adjust KEYWORDS list.
	▪	Modify POLL_INTERVAL (in seconds) or WHISPER_MODEL (e.g., “large” for better accuracy, but slower).
	▪	Set language in transcription if not English.
	3	Counter Initialization:
	◦	The script handles this automatically, but you can manually upload a counter.txt file with “0” to the main Google Drive folder if needed.
Usage
	1	Run the Script: python tiktok_automator.py
	2	
	◦	The script will start polling and log status to the console.
	◦	When a live is detected, it records, processes, and uploads files.
	3	Running in Background:
	◦	On Linux (using tmux): tmux new -s automator
	◦	source venv/bin/activate
	◦	python tiktok_automator.py
	◦	 Detach with Ctrl+B, D; reattach with tmux attach -t automator.
	◦	As a systemd service (on Linux): Create /etc/systemd/system/tiktok.service with the content provided in the setup guide, then: sudo systemctl daemon-reload
	◦	sudo systemctl start tiktok.service
	◦	sudo systemctl enable tiktok.service
	◦	
	4	Output Structure in Google Drive:
	◦	Main Folder (e.g., “TikTokLives”)
	▪	Date Folder (e.g., “2025-08-04”)
	▪	1-Official_Allmoney_04-2025-08-04-120000-video.mp4
	▪	1-Official_Allmoney_04-2025-08-04-120000-transcription.docx
	▪	1-Official_Allmoney_04-2025-08-04-120000-keywords.xlsx
	▪	counter.txt (internal use)
	5	Stopping the Script:
	◦	Ctrl+C in the terminal.
	◦	For services: sudo systemctl stop tiktok.service.
Troubleshooting
	•	Live Detection Fails: Ensure TikTokLive is up-to-date; TikTok may change APIs. Check console logs for errors.
	•	Recording Issues: Verify Streamlink and FFmpeg are in PATH. Test manually: streamlink https://www.tiktok.com/@Official_Allmoney_04/live best.
	•	Transcription Slow: Use a smaller Whisper model (“tiny”) or run on a machine with more CPU/GPU.
	•	Google Drive Errors: Check service account permissions and API quota. Verify service.json is correct.
	•	File Size Limits: Google Drive handles large files, but very long streams may need splitting (not implemented).
	•	Dependencies Conflicts: Use a clean virtual environment.
	•	Logs: Add Python’s logging module to the script for file-based logs if needed.
Contributing
Feel free to fork and submit pull requests for improvements, such as adding email notifications or multi-user support.
License
This project is licensed under the MIT License. See LICENSE file for details (create one if needed).
Acknowledgments
	•	Built with open-source tools: TikTokLive, Streamlink, Whisper, Google API Client.
	•	Inspired by needs for content archiving and analysis.

requirements.txt
TikTokLive
streamlink
whisper-timestamped
python-docx
pandas
google-api-python-client
google-auth
google-auth-oauthlib
torch
torchaudio

