import datetime
import os

import pytz
from googleapiclient.discovery import build


def generate_markdown(videos):
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')

    md_lines = []
    md_lines.append(f"# {date_str} {time_str} (JST)")
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
