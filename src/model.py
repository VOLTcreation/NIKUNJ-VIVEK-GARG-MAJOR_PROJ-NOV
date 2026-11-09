import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 1. Database Connection
load_dotenv()
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "youtube_analytics")

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

def generate_virality_scores():
    print("📥 Fetching video metrics for statistical modeling...")
    df = pd.read_sql("SELECT * FROM videos;", con=engine)
    
    if df.empty:
        print("⚠️ No video data found.")
        return

    # 2. Calculate the Raw Viral Coefficient
    # Rubric constraint: Weigh high-value actions (Comments) heavier than passive actions (Likes)
    df["raw_viral_score"] = ((df["comment_count"] * 2.5) + df["like_count"]) / df["view_count"]

    # 3. Scikit-Learn Statistical Normalization
    if len(df) > 1:
        # If multiple videos exist, compare them against each other
        scaler = MinMaxScaler(feature_range=(0, 100))
        df["viral_coefficient"] = scaler.fit_transform(df[["raw_viral_score"]])
    else:
        # If only 1 video exists, calculate an absolute benchmark (Raw Score mapped to 100)
        df["viral_coefficient"] = df["raw_viral_score"] * 1000
        # Cap the maximum score at 100.0
        df.loc[df["viral_coefficient"] > 100, "viral_coefficient"] = 100.0

    # Round for clean UI presentation
    df["viral_coefficient"] = df["viral_coefficient"].round(2)

    # 4. Save to a new database table
    virality_df = df[["video_id", "title", "raw_viral_score", "viral_coefficient"]]
    virality_df.to_sql(name="virality_metrics", con=engine, if_exists="replace", index=False)
    
    print("✅ Scikit-Learn Virality Model executed successfully!")
    print(virality_df[["title", "viral_coefficient"]].to_string())

if __name__ == "__main__":
    generate_virality_scores()