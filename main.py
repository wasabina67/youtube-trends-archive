import datetime
import os

import pytz
from googleapiclient.discovery import build


def generate_markdown(videos):
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    year_str = now.strftime('%Y')
    month_day_str = now.strftime('%m%d')

    md_lines = []
    md_lines.append(f"## {date_str} {time_str}")
    md_lines.append("")

    for i, video in enumerate(videos, 1):
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        video_id = video.get('id', '')

        title = snippet.get('title', 'No Title')
        channel_title = snippet.get('channelTitle', 'Unknown Channel')
        view_count = int(statistics.get('viewCount', '0'))
        like_count = int(statistics.get('likeCount', '0'))
        comment_count = int(statistics.get('commentCount', '0'))

        md_lines.append(f"### {title}")
        md_lines.append("")
        md_lines.append(f"- **Channel:** {channel_title}")
        md_lines.append(f"- **URL:** [https://www.youtube.com/watch?v={video_id}](https://www.youtube.com/watch?v={video_id})")  # noqa
        md_lines.append("")
        md_lines.append(f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>')  # noqa
        md_lines.append("")
        md_lines.append(f"{view_count:,} views | {like_count:,} likes | {comment_count:,} comments")
        md_lines.append("")

    output_dir = f'docs/{year_str}'
    os.makedirs(output_dir, exist_ok=True)

    output_path = f'{output_dir}/{month_day_str}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))


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
