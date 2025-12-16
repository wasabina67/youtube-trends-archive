import datetime  # noqa
import os

import pytz  # noqa
from googleapiclient.discovery import build


def generate_markdown(videos):
    print(videos)


def get_trending_videos(api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode='JP',
        maxResults=10,
    )
    return request.execute().get('items', [])


def main():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY is not set")
        return

    try:
        print("Fetching trending videos...")
        videos = get_trending_videos(api_key)

        generate_markdown(videos)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
