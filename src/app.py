import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 1. Page Configuration
st.set_page_config(page_title="Social Engagement Dashboard", page_icon="📊", layout="wide")

# 2. Database Connection
load_dotenv()
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "youtube_analytics")

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

# 3. Data Loading Function
@st.cache_data(ttl=60) # Caches data for 60 seconds to prevent constant DB hits
def load_data():
    try:
        videos_df = pd.read_sql("SELECT * FROM videos;", con=engine)
        comments_df = pd.read_sql("SELECT * FROM analyzed_comments;", con=engine)
        virality_df = pd.read_sql("SELECT * FROM virality_metrics;", con=engine)
        return videos_df, comments_df, virality_df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

videos_df, comments_df, virality_df = load_data()

# 4. Dashboard Header
st.title("📊 Social Engagement & Virality Dashboard")
st.markdown("Live YouTube Metrics and NLP Sentiment Analysis")
st.divider()

# 5. Video Metrics Section
if not videos_df.empty and not virality_df.empty:
    st.subheader("🎬 Latest Video Performance")
    # Sort by viral coefficient descending to show the top performing video
    top_video_row = virality_df.sort_values(by="viral_coefficient", ascending=False).iloc[0]
    video_id = top_video_row["video_id"]

    latest_video = videos_df[videos_df["video_id"] == video_id].iloc[0]
    latest_virality = top_video_row
    
    st.write(f"**{latest_video['title']}** — {latest_video['channel']}")
    
    # Create 4 metric cards side-by-side
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Views", f"{latest_video['view_count']:,}")
    col2.metric("Total Likes", f"{latest_video['like_count']:,}")
    col3.metric("Total Comments", f"{latest_video['comment_count']:,}")
    col4.metric("🔥 Viral Coefficient (0-100)", f"{latest_virality['viral_coefficient']}")
else:
    st.warning("No video data found in the database.")

st.divider()

# 6. Sentiment Analysis Section
if not comments_df.empty:
    col_chart, col_data = st.columns([1, 2])
    
    with col_chart:
        st.subheader("🧠 Audience Sentiment")
        # Count sentiment labels and plot a bar chart
        sentiment_counts = comments_df["sentiment_label"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        
        # Color mapping for visual clarity
        st.bar_chart(sentiment_counts.set_index("Sentiment"))
        
    with col_data:
        st.subheader("💬 Analyzed Comment Feed")
        # Display an interactive dataframe sorting comments by polarity
        display_df = comments_df[["author", "sentiment_label", "polarity", "comment_text"]]
        
        # Updated to width="stretch" to clear the Streamlit deprecation warning
        st.dataframe(display_df, width="stretch", hide_index=True, height=350)
else:
    st.warning("No comment sentiment data found in the database.")