# app.py
from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from textblob import TextBlob
import os
import re
from datetime import datetime

app = Flask(__name__)

# Konfigurasi
API_KEY = "AIzaSyBrGUzP5IN7wOIfzpbaboonPqJlBrpUFm8"  # Ganti dengan API key Anda

def detect_gambling_content(text):
    # Daftar kata kunci dan pola untuk mendeteksi konten perjudian
    gambling_keywords = [
        r'pulau\s*7+', r'jepe\s*gaspol', r'jakpot', r'depo\s*receh', 
        r'mekswin', r'rezeki', r'a[a-zA-Z]*x[a-zA-Z]*l\s*\d+', 
        r'as[a-zA-Z]*k[a-zA-Z]*to[a-zA-Z]*to', r'd[a-zA-Z]*[o0][a-zA-Z]*ra\s*\d+',
        r'a[a-zA-Z]*hm[a-zA-Z]*d[a-zA-Z]*t[a-zA-Z]*[o0][a-zA-Z]*t[a-zA-Z]*[o0]',
        r'ag[a-zA-Z]*st[a-zA-Z]*[o0][a-zA-Z]*t[a-zA-Z]*[o0]',
        r'a[a-zA-Z]*[eеэ][a-zA-Z]*r[a-zA-Z]*[o0]\s*\d+'
    ]
    
    # Cek apakah teks mengandung pola perjudian
    for pattern in gambling_keywords:
        if re.search(pattern, text.lower()):
            return True
    
    # Cek karakteristik lain dari komen perjudian:
    # 1. Menggabungkan huruf dan angka dengan cara tidak wajar
    if re.search(r'[a-zA-Z]+\d+\d+\d+', text):
        return True
    
    # 2. Penggunaan karakter khusus untuk menyamarkan teks
    if re.search(r'[𝐀-𝐙𝑨-𝒁𝓐-𝓩𝔸-𝕐𝕬-𝖅𝖠-𝖹𝗔-𝗭𝘼-𝙕𝙰-𝚉]', text):
        return True
    
    return False

def analyze_sentiment(text):
    # Cek terlebih dahulu apakah ini adalah konten perjudian
    if detect_gambling_content(text):
        return "judol"
    
    # Jika bukan, lakukan analisis sentimen reguler
    analysis = TextBlob(text)
    # Menentukan sentimen berdasarkan polarity
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"

def get_youtube_comments(channel_name, video_title):
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        # Cari channel ID
        channel_response = youtube.search().list(
            q=channel_name,
            type='channel',
            part='id',
            maxResults=1
        ).execute()
        
        if not channel_response['items']:
            return {"error": "Channel tidak ditemukan"}
            
        channel_id = channel_response['items'][0]['id']['channelId']
        
        # Cari video
        video_response = youtube.search().list(
            q=video_title,
            channelId=channel_id,
            type='video',
            part='id,snippet',
            maxResults=1
        ).execute()
        
        if not video_response['items']:
            return {"error": "Video tidak ditemukan"}
            
        video_id = video_response['items'][0]['id']['videoId']
        video_info = video_response['items'][0]['snippet']
        
        # Inisialisasi counter
        sentiment_stats = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "judol": 0,  # Tambahkan kategori untuk judol
            "total": 0
        }
        
        # Ambil komentar
        comments = []
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            # maxResults=1000
        )
        
        while request:
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                published_at = datetime.strptime(comment['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = published_at.strftime("%d %b %Y %H:%M")
                
                # Analisis sentimen
                sentiment = analyze_sentiment(comment['textDisplay'])
                sentiment_stats[sentiment] += 1
                sentiment_stats["total"] += 1
                
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'published_at': formatted_date,
                    'sentiment': sentiment
                })
                
            request = youtube.commentThreads().list_next(request, response)
        
        return {
            "success": True,
            "video_info": {
                "title": video_info['title'],
                "thumbnail": video_info['thumbnails']['default']['url'],
                "channel": video_info['channelTitle']
            },
            "comments": comments,
            "sentiment_stats": sentiment_stats
        }
        
    except HttpError as e:
        return {"error": f"Terjadi error: {str(e)}"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-comments', methods=['POST'])
def fetch_comments():
    data = request.json
    channel_name = data.get('channel_name')
    video_title = data.get('video_title')
    
    if not channel_name or not video_title:
        return jsonify({"error": "Channel name dan video title harus diisi"})
    
    result = get_youtube_comments(channel_name, video_title)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)