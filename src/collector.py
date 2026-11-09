import os
import pandas as pd
from urllib.parse import quote_plus  # URL encoder for passwords containing '@'
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# MySQL Configuration
DB_USER = os.getenv("DB_USER", "root")
raw_password = os.getenv("DB_PASSWORD", "")
DB_PASSWORD = quote_plus(raw_password)  # Safely encodes your '@' symbol
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "youtube_analytics")

if not API_KEY or API_KEY == "your_youtube_api_key_here":
    raise ValueError("YOUTUBE_API_KEY is missing. Check your .env file.")

# Initialize YouTube client & Database Engine
youtube = build("youtube", "v3", developerKey=API_KEY)
db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)


def get_video_metrics(video_id: str) -> pd.DataFrame:
    """Fetches core performance metrics and formats timestamps for MySQL."""
    try:
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()

        if not response.get("items"):
            print(f"[WARNING] No data found for video ID: {video_id}")
            return pd.DataFrame()

        item = response["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]

        # Parse datetime and strip the timezone for MySQL compatibility
        raw_date = pd.to_datetime(snippet.get("publishedAt"))
        clean_date = raw_date.tz_convert(None) if raw_date.tzinfo else raw_date

        data = [{
            "video_id": video_id,
            "title": snippet.get("title"),
            "channel": snippet.get("channelTitle"),
            "published_at": clean_date,
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0))
        }]
        
        return pd.DataFrame(data)
    
    except HttpError as e:
        print(f"[ERROR] API failed to fetch metrics: {e}")
        return pd.DataFrame()


def get_video_comments(video_id: str, max_comments: int = 100) -> pd.DataFrame:
    """Fetches top-level comments and formats timestamps for MySQL."""
    comments = []
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments),
            order="relevance",
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
            
            # Parse datetime and strip the timezone for MySQL compatibility
            raw_date = pd.to_datetime(comment_snippet.get("publishedAt"))
            clean_date = raw_date.tz_convert(None) if raw_date.tzinfo else raw_date

            comments.append({
                "video_id": video_id,
                "author": comment_snippet.get("authorDisplayName"),
                "comment_text": comment_snippet.get("textOriginal"),
                "like_count": comment_snippet.get("likeCount", 0),
                "published_at": clean_date
            })

        return pd.DataFrame(comments)
    
    except HttpError as e:
        if "commentsDisabled" in str(e):
            print(f"[WARNING] Comments are disabled for video ID: {video_id}")
        else:
            print(f"[ERROR] API failed to fetch comments: {e}")
        return pd.DataFrame()


def save_to_mysql(metrics_df: pd.DataFrame, comments_df: pd.DataFrame):
    """Writes the extracted DataFrames directly into MySQL tables cleanly."""
    try:
        with engine.begin() as connection:
            # Temporarily disable foreign key checks, clear tables, and re-enable
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            connection.execute(text("DELETE FROM comments;"))
            connection.execute(text("DELETE FROM videos;"))
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

            if not metrics_df.empty:
                metrics_df.to_sql(name="videos", con=connection, if_exists="append", index=False)
                print(f"✅ Successfully saved metrics to MySQL 'videos' table.")
            
            if not comments_df.empty:
                comments_df.to_sql(name="comments", con=connection, if_exists="append", index=False)
                print(f"✅ Successfully saved {len(comments_df)} comments to MySQL 'comments' table.")
    except Exception as e:
        print(f"❌ Database error: {e}")


if __name__ == "__main__":
    SAMPLE_VIDEO_ID = "IT6svoR9M-0"  # Change this to test any YouTube video ID
    print(f"Extracting and storing data for: {SAMPLE_VIDEO_ID}...\n")
    
    # 1. Extract
    metrics_df = get_video_metrics(SAMPLE_VIDEO_ID)
    comments_df = get_video_comments(SAMPLE_VIDEO_ID, max_comments=50)
    
    # 2. Load into Database
    save_to_mysql(metrics_df, comments_df)