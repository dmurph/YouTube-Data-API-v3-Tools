import os
import logging

from youtube_api_tools import YouTubeDataAPIv3Tools

# --- Configuration ---
# 1. Set the path to your client_secret.json file.
CLIENT_SECRET_FILE = 'client_secret.json' # Assumes it's in the same directory

# 2. Define the scopes. To read captions, you'll need a scope that allows YouTube access.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl', 'https://www.googleapis.com/auth/youtube.readonly']

# 3. Set the ID of the video you want to get captions for.
VIDEO_ID = 'BJJoPOXIxUo' # Example: Google's Super Bowl 2024 Ad

def main():
    """
    Initializes the YouTube API tools, fetches, and prints caption tracks for a video.
    """
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: The client secret file was not found at '{CLIENT_SECRET_FILE}'")
        print("Please place your client_secret.json in the same directory as this script, or update the CLIENT_SECRET_FILE path.")
        return

    print("Initializing YouTubeDataAPIv3Tools...")
    # Initialize the main class
    youtube_tools = YouTubeDataAPIv3Tools(CLIENT_SECRET_FILE, SCOPES)

    print(f"\nFetching caption tracks for video ID: {VIDEO_ID}")
    try:
        # Access the Captions subclass
        captions_handler = youtube_tools.Captions(youtube_tools)

        # Fetch the caption tracks for the specified video.
        caption_tracks = captions_handler.get_all_track_ids( video_id=VIDEO_ID)
        for id in caption_tracks:
          logging.error(id)

        # if caption_tracks and 'items' in caption_tracks and caption_tracks['items']:
        #     print("\nAvailable Caption Tracks:")
        #     for track in caption_tracks['items']:
        #         snippet = track.get('snippet', {})
        #         lang = snippet.get('language', 'N/A')
        #         name = snippet.get('name', 'No Name')
        #         track_kind = snippet.get('trackKind', 'standard')
        #         print(f"- Language: {lang}, Name: '{name}', Kind: {track_kind}")
        # else:
        #     print("\nNo caption tracks found for this video.")

    except Exception as e:
        logging.exception(f"\nAn error occurred: {e}")
        logging.info("This could be due to incorrect scopes, an invalid video ID, or the video having no captions.")

if __name__ == '__main__':
    main()
