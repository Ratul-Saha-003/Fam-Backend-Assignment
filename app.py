from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, APIKey
from services import fetch_latest_videos, save_videos_to_db, get_paginated_videos, add_api_key, get_all_videos, get_videos_by_title
import threading
import time
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# env variables
INTERVAL = os.getenv("INTERVAL")
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLite DB
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Background thread which fetches videos with a given interval
def background_fetch():
    while True:
        session = SessionLocal()
        try:
            videos = fetch_latest_videos(session)
            print(videos)
            save_videos_to_db(session, videos)
            print("Done")
        finally:
            session.close()
        time.sleep(INTERVAL)

# Base route
@app.route('/')
def index():
    return "YouTube Video Fetcher Running..."

# Fetch all videos for displaying in the dashboard
@app.route('/dashboard', methods=['GET'])
def view_dashboard():
    session = SessionLocal()
    try:
        videos = get_all_videos(session)
        # rendering template with all the videos
        return render_template("index.html", videos=videos)
    finally:
        session.close()

# Fetch filtered out videos based on title string
@app.route('/filter-dashboard', methods=['GET'])
def search_videos():
    title = request.args.get('search',"")
    session = SessionLocal()
    if not title:
        videos = get_all_videos(session)
        # rendering template with all the videos if no title is present
        return render_template("index.html", videos=videos)

    try:
        result = get_videos_by_title(session, title)
        # rendering template with filtered-out videos if title is present
        return render_template("index.html", videos=result)
    finally:
        session.close()



# GET route for returning paginated videos
@app.route('/videos', methods=['GET'])
def get_videos():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    session = SessionLocal()
    try:
        videos = get_paginated_videos(session, page, per_page)
        return jsonify(videos)
    finally:
        session.close()

# Adding API Keys to the table
@app.route('/api-keys', methods=['POST'])
def handle_add_api_key():
    data = request.get_json()
    key = data.get('key')
    # Checking if key exists in request
    if not key:
        return jsonify({"error": "API key is required"}), 400
    session = SessionLocal()
    try:
        message, status = add_api_key(session, key)
        return jsonify({"message": message}), status
    finally:
        session.close()



if __name__ == '__main__':
    # Start background fetcher thread
    thread = threading.Thread(target=background_fetch, daemon=True)
    thread.start()
    app.run(debug=True)