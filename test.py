from flask import Flask, request, render_template
import requests
import re

app = Flask(__name__)

API_KEY = "AIzaSyBrGUzP5IN7wOIfzpbaboonPqJlBrpUFm8"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

# List of keywords indicating gambling/spam comments
SPAM_KEYWORDS = ["P U L A U 7 7 7", "jepe gaspol", "jakpot", "АСИКТОТО", "DORА", "AHMADTOTO", "AGUSTOTO", "AERO88"]

def get_comments(video_id):
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": API_KEY,
        "maxResults": 100
    }
    response = requests.get(YOUTUBE_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []

def detect_spam_comments(comments):
    detected = []
    for comment in comments:
        text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        if any(re.search(keyword, text, re.IGNORECASE) for keyword in SPAM_KEYWORDS):
            detected.append(text)
    return detected

@app.route("/", methods=["GET", "POST"])
def index():
    comments, spam_comments = [], []
    video_id = ""
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if "youtube.com/watch?v=" in video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]
            comments = get_comments(video_id)
            spam_comments = detect_spam_comments(comments)
    return render_template("index.html", video_id=video_id, total_comments=len(comments), spam_count=len(spam_comments), spam_comments=spam_comments)

if __name__ == "__main__":
    app.run(debug=True)