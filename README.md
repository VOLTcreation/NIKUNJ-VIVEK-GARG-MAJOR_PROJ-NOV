# 📊 YouTube Analytics & Virality Predictor Dashboard

A full-stack, end-to-end Data Science pipeline and real-time analytical dashboard built to extract YouTube video performance metrics, compute audience sentiment dynamics using NLP, and evaluate content virality through statistical normalization.

---

## 📌 Project Architecture & Pipeline Flow

The system operates via a decoupled four-stage modular data architecture:

```
[ YouTube API v3 ]
       │
       ▼
 1. Data Collector (src/collector.py)
       │ ──► [ MySQL Database: 'videos', 'comments' ]
       ▼
 2. Sentiment Engine (src/sentiment.py)
       │ ──► [ TextBlob NLP Analysis ] ──► [ MySQL: 'analyzed_comments' ]
       ▼
 3. Virality Model (src/model.py)
       │ ──► [ Scikit-Learn MinMaxScaler ] ──► [ MySQL: 'virality_metrics' ]
       ▼
 4. Interactive Dashboard (src/app.py)
         ──► [ Streamlit UI Visualization ]
```

1. **Data Extraction (`src/collector.py`)**: Queries the YouTube Data API v3 for video statistics (views, likes, comments) and top-level comment threads. Manages database transactions and cleans stale records.
2. **NLP Sentiment Processing (`src/sentiment.py`)**: Reads stored comments from MySQL, calculates sentiment polarity using TextBlob, and categorizes feedback into *Relatable*, *Neutral*, or *Negative*.
3. **Statistical Modeling (`src/model.py`)**: Applies mathematical weighting ($2.5\times$ multiplier on comments vs. likes) to measure audience engagement intensity, then normalizes the raw score using `scikit-learn`'s `MinMaxScaler` on a scale of 0.00 to 100.00.
4. **Dashboard Presentation (`src/app.py`)**: A Streamlit frontend that renders real-time metric cards, sentiment distribution charts, and analyzed comment feeds directly from MySQL.

---

## ✨ Key Features

* **Live Data Pipeline**: Bypasses static CSVs by pulling real-time metadata directly via YouTube API v3.
* **Robust Edge-Case Handling**: 
  * Automatically detects and handles videos with disabled comments or livestreams without crashing.
  * Cleans URL query parameters (timestamps, playlists) to isolate valid 11-character YouTube video IDs.
  * Solves single-video `MinMaxScaler` zero-variance edge cases by applying an absolute benchmark fallback when comparative video datasets are absent.
* **Relational Database Sync**: Implements clean foreign key management and automated table resets (`DELETE FROM`) across `videos`, `comments`, `analyzed_comments`, and `virality_metrics` to guarantee zero data leakage between test runs.
* **Weighted Virality Scoring**: Employs a custom heuristic that heavily favors high-intent user actions (comments) over passive engagement (likes) relative to total views.

---

## 🛠️ Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core programming language |
| **Database** | MySQL, SQLAlchemy, PyMySQL | Relational storage and ORM connection management |
| **Data Processing** | Pandas, NumPy | Data cleaning, transformation, and structured formatting |
| **Machine Learning** | Scikit-Learn (`MinMaxScaler`) | Statistical normalization of engagement metrics |
| **NLP** | TextBlob | Sentiment polarity scoring and qualitative classification |
| **Frontend** | Streamlit | Interactive web user interface and chart rendering |
| **API** | Google API Client Library (`googleapiclient`) | Live YouTube Data API v3 integration |
| **Config** | `python-dotenv` | Secure environment variable management |

---

## 🗄️ Database Schema Structure

The MySQL database (`youtube_analytics`) consists of four primary relational tables:

* `videos`: `video_id` (PRIMARY KEY), `title`, `channel`, `published_at`, `view_count`, `like_count`, `comment_count`
* `comments`: `id` (AUTO INCREMENT PRIMARY KEY), `video_id` (FOREIGN KEY), `author`, `comment_text`, `like_count`, `published_at`
* `analyzed_comments`: Stores TextBlob output (`sentiment_label`, `polarity`) joined with comment metadata.
* `virality_metrics`: Stores raw viral calculations and final `viral_coefficient` (score from $0$ to $100$).

---

## 🚀 Getting Started & Installation

### 1. Prerequisites
* Python 3.10 or higher installed.
* MySQL Server running locally on port `3306`.
* Google Cloud Console account with **YouTube Data API v3** enabled and an API key generated.

### 2. Repository Setup
```bash
# Clone the repository
git clone https://github.com/VOLTcreation/Social_Connect_project.git
cd Social_Connect_project

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Dependencies Installation
```bash
pip install pandas scikit-learn textblob sqlalchemy pymysql streamlit python-dotenv google-api-python-client
```

### 4. Environment Configuration
Create a `.env` file in the project root directory with the following variables:

```env
YOUTUBE_API_KEY=your_actual_youtube_api_key_here
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=youtube_analytics
```

### 5. MySQL Database Initialization
Open MySQL Workbench or your SQL terminal and create the database schema:
```sql
CREATE DATABASE IF NOT EXISTS youtube_analytics;
```

---

## 💻 Execution Workflow

To run the complete data extraction and modeling pipeline for a video, execute the following scripts in order:

```bash
# Stage 1: Extract data from YouTube API & store in MySQL
python src/collector.py

# Stage 2: Perform NLP sentiment analysis on comments
python src/sentiment.py

# Stage 3: Run Scikit-Learn Virality Model & score calculation
python src/model.py

# Stage 4: Launch the Streamlit Web Application
streamlit run src/app.py
```



---

## 🔮 Future Scope & System Roadmap

While the current architecture serves as an efficient single-video analytics engine, the system design is prepared for expansion into an enterprise multi-video intelligence suite:

1. **Historical Relative Benchmarking**: Transitioning from table truncation to persistent video logging, allowing Scikit-Learn to evaluate new videos against channel-specific percentile distributions.
2. **Comparative Sentiment Dynamics**: Tracking shifts in audience sentiment (*Relatable* vs. *Neutral* ratio) across different content genres (e.g., Tutorials vs. Gaming vs. Music).
3. **Virality Driver Analysis**: Performing regression modeling to determine whether high positive sentiment or high comment polarity serves as a stronger statistical predictor of viral reach.
4. **Side-by-Side A/B Matrix**: Adding a multi-video comparison interface in Streamlit to analyze metric deltas ($\Delta$) between multiple uploads simultaneously.
5. **Automated Content Strategy Engine**: Generating heuristic content recommendations based on aggregated sentiment patterns and engagement density thresholds.

---

## 👨‍💻 Author

**Nikunj Garg**  
*B.Tech Computer Science and Engineering (Data Science)*  
* Chandigarh University  
* GitHub: [@VOLTcreation](https://github.com/VOLTcreation)  
* Core Philosophy: *LEARN • BUILD • SHARE*

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.