import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
raw_password = os.getenv("DB_PASSWORD", "")
DB_PASSWORD = quote_plus(raw_password)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "youtube_analytics")

def init_db():
    """Initializes the database and creates required tables."""
    # 1. Connect to MySQL base to ensure the database exists
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    engine_base = create_engine(base_url)
    
    with engine_base.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
        print(f"[SUCCESS] Database '{DB_NAME}' ensured.")

    # 2. Connect directly to the new database to build tables
    db_url = f"{base_url}{DB_NAME}"
    engine = create_engine(db_url)
    
    create_videos_table = """
    CREATE TABLE IF NOT EXISTS videos (
        video_id VARCHAR(50) PRIMARY KEY,
        title VARCHAR(255),
        channel VARCHAR(255),
        published_at DATETIME,
        view_count BIGINT,
        like_count INT,
        comment_count INT,
        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_comments_table = """
    CREATE TABLE IF NOT EXISTS comments (
        comment_id INT AUTO_INCREMENT PRIMARY KEY,
        video_id VARCHAR(50),
        author VARCHAR(255),
        comment_text TEXT,
        like_count INT,
        published_at DATETIME,
        FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_videos_table))
        conn.execute(text(create_comments_table))
        print("[SUCCESS] Tables 'videos' and 'comments' are ready!")

if __name__ == "__main__":
    init_db()