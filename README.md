# 🎥 YouTube Comment Analyzer | Sentiment + Gambling Detector 🎰

A simple web application built with Flask to analyze YouTube video comments, detect sentiment (positive, negative, neutral), and flag potential gambling (judol) content automatically.

---

## ✨ Features
- ✅ Analyze YouTube video comments by channel and video title
- ✅ Sentiment detection (Positive, Negative, Neutral)
- ✅ Gambling-related comment detection (judol detector)
- ✅ Simple API endpoint to get analyzed comments
- ✅ Display comment list with sentiment badges and published date

---

## ⚙️ Tech Stack
- Python
- Flask
- Google YouTube API
- TextBlob (Sentiment Analysis)
- Regex (Gambling Detection)

---

## 🛠️ Installation

1. Clone this repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Replace API_KEY in app.py with your own YouTube Data API Key
```bash
API_KEY = "YOUR_YOUTUBE_API_KEY"
```
6. Run the application
```bash
python app.py
```

## 🔄 API Endpoint
POST /get-comments

Request Body (JSON):
```bash
{
    "channel_name": "channel name here",
    "video_title": "video title here"
}
```

Response:
```bash
{
    "success": true,
    "video_info": {
        "title": "Video Title",
        "thumbnail": "thumbnail_url",
        "channel": "Channel Name"
    },
    "comments": [
        {
            "author": "Author Name",
            "text": "Comment Text",
            "likes": 5,
            "published_at": "27 Mar 2025 14:21",
            "sentiment": "positive"
        },
        ...
    ],
    "sentiment_stats": {
        "positive": 5,
        "negative": 2,
        "neutral": 10,
        "judol": 1,
        "total": 18
    }
}
```
