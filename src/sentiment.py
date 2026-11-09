import os
import pandas as pd
from textblob import TextBlob
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL Configuration (with @ symbol password fix)
DB_USER = os.getenv("DB_USER", "root")
raw_password = os.getenv("DB_PASSWORD", "")
DB_PASSWORD = quote_plus(raw_password)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "youtube_analytics")

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

def analyze_sentiment(text: str) -> dict:
    """Calculates sentiment polarity and assigns a relatability label."""
    if not text or pd.isna(text):
        return {"polarity": 0.0, "subjectivity": 0.0, "sentiment_label": "Neutral"}
    
    analysis = TextBlob(str(text))
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    # Categorization logic for the project deliverables
    if polarity > 0.1 and subjectivity > 0.3:
        label = "Relatable"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "sentiment_label": label
    }

def process_and_save_sentiments():
    print("📥 Fetching raw comments from MySQL...")
    
    # 1. Load comments directly from MySQL into a Pandas DataFrame
    query = "SELECT comment_id, video_id, author, comment_text, like_count FROM comments;"
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        print("⚠️ No comments found in the database. Run collector.py first.")
        return

    print(f"🧠 Analyzing sentiment for {len(df)} comments...")
    
    # 2. Apply TextBlob sentiment analysis to the 'comment_text' column
    sentiment_results = df["comment_text"].apply(analyze_sentiment)
    sentiment_df = pd.DataFrame(sentiment_results.tolist())
    
    # 3. Combine original data with the new sentiment scores
    processed_df = pd.concat([df, sentiment_df], axis=1)
    
    # 4. Save the expanded DataFrame back to MySQL in a new table
    processed_df.to_sql(name="analyzed_comments", con=engine, if_exists="replace", index=False)
    
    print("✅ Successfully saved sentiment analysis to 'analyzed_comments' table!")
    print("\n--- Sentiment Summary ---")
    print(processed_df["sentiment_label"].value_counts().to_string())

if __name__ == "__main__":
    process_and_save_sentiments()