import datetime
import os

import pytz
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CATEGORY_NEWS_POLITICS = 25
CATEGORY_EDUCATION = 27
CATEGORY_SCIENCE_TECH = 28

CATEGORY_NAMES = {
    CATEGORY_NEWS_POLITICS: "News & Politics",
    CATEGORY_EDUCATION: "Education",
    CATEGORY_SCIENCE_TECH: "Science & Technology",
}


def update_index(year_str, month_day_str):
    index_path = "docs/index.md"
    new_entry = f"- [./{year_str}/{month_day_str}.md](./{year_str}/{month_day_str}.md)"

    existing_entries = []
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            existing_entries = [line.strip() for line in f if line.strip()]

    if new_entry not in existing_entries:
        existing_entries.append(new_entry)

    existing_entries.sort(reverse=True)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(existing_entries))
        f.write("\n")


def generate_markdown(videos):
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.datetime.now(jst)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    year_str = now.strftime("%Y")
    month_day_str = now.strftime("%m%d")

    md_lines = []
    md_lines.append(f"## {date_str} {time_str}")
    md_lines.append("")

    for _, video in enumerate(videos, 1):
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        video_id = video.get("id", "")

        title = snippet.get("title", "No Title")
        channel_title = snippet.get("channelTitle", "Unknown Channel")
        view_count = int(statistics.get("viewCount", "0"))
        like_count = int(statistics.get("likeCount", "0"))
        comment_count = int(statistics.get("commentCount", "0"))

        md_lines.append(f"### {title}")
        md_lines.append("")
        md_lines.append(f"- {channel_title}")
        md_lines.append(f"- [https://www.youtube.com/watch?v={video_id}](https://www.youtube.com/watch?v={video_id})")  # noqa
        md_lines.append("")
        md_lines.append(
            f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'  # noqa
        )
        md_lines.append("")
        md_lines.append(f"{view_count:,} views | {like_count:,} likes | {comment_count:,} comments")
        md_lines.append("")

    output_dir = f"docs/{year_str}"
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/{month_day_str}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    update_index(year_str, month_day_str)


def get_trending_videos(api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    category_ids = [
        CATEGORY_NEWS_POLITICS,
        CATEGORY_EDUCATION,
        CATEGORY_SCIENCE_TECH,
    ]
    all_videos = []
    seen_video_ids = set()

    # Fetch videos from each category
    for category_id in category_ids:
        try:
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="JP",
                videoCategoryId=category_id,
                maxResults=10,
            )
            response = request.execute()
            videos = response.get("items", [])

            # Add unique videos
            for video in videos:
                video_id = video.get("id")
                if video_id and video_id not in seen_video_ids:
                    seen_video_ids.add(video_id)
                    all_videos.append(video)
        except HttpError as e:
            category_name = CATEGORY_NAMES.get(category_id, f"ID {category_id}")
            print(f"Warning: Failed to fetch videos for category {category_name}: {e}")
            continue

    # Sort by view count (highest first) and return top 10
    def get_view_count(video):
        try:
            return int(video.get("statistics", {}).get("viewCount", "0"))
        except (ValueError, TypeError):
            return 0

    all_videos.sort(key=get_view_count, reverse=True)
    return all_videos[:10]


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
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
