import time
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import ssl
import urllib3

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

api = None
live_chat_id = None

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_authenticated_service():
    global api
    if api is None:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        credentials = flow.run_local_server(port=0)
        api = build("youtube", "v3", credentials=credentials)
    return api

def get_live_chat_id():
    global live_chat_id
    api = get_authenticated_service()

    url = input("🔗 Enter YouTube Live Stream URL: ").strip()
    video_id = extract_video_id(url)
    if not video_id:
        print("❌ Invalid YouTube video URL.")
        return None

    response = api.videos().list(part="liveStreamingDetails", id=video_id).execute()
    items = response.get("items", [])
    if items:
        live_chat_id = items[0]["liveStreamingDetails"].get("activeLiveChatId")
        if live_chat_id:
            print("✅ Live chat ID fetched successfully.")
        else:
            print("❌ No active live chat found.")
    return live_chat_id

def get_messages():
    api = get_authenticated_service()
    live_chat_id = get_live_chat_id()
    if not live_chat_id:
        return

    next_page_token = None

    while True:
        try:
            response = api.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet,authorDetails",
                pageToken=next_page_token
            ).execute()

            for item in response.get("items", []):
                text = item["snippet"]["displayMessage"]
                author = item["authorDetails"]["displayName"]
                yield (author, text)

            next_page_token = response.get("nextPageToken")
            polling_interval = int(response.get("pollingIntervalMillis", 2000)) / 1000.0
            time.sleep(polling_interval)

        except HttpError as e:
            print("❌ HTTP Error:", e)
            if "403" in str(e):
                print("⏳ Waiting due to rate limit...")
                time.sleep(5)
            else:
                break
        except ssl.SSLError as ssl_error:
            print("❌ SSL Error:", ssl_error)
            print("⏳ Retrying in 10 seconds...")
            time.sleep(10)
        except Exception as e:
            print("❌ Unknown error:", e)
            break
