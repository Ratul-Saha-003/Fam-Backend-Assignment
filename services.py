import requests
from datetime import datetime
from models import Video, APIKey
from sqlalchemy.orm import Session
import logging
from sqlalchemy import or_
from datetime import datetime
import os
from sqlalchemy.dialects.mysql import insert
from dotenv import load_dotenv

load_dotenv()

SEARCH_QUERY = os.getenv("SEARCH_QUERY")
SEARCH_URL = os.getenv("SEARCH_URL")
VIDEO_FIELDS = ['snippet']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_published_time(session: Session):
    '''
    Returns the published time of the latest video in the database
    '''
    latest_video = session.query(Video).order_by(Video.published_at.desc()).first()
    return latest_video.published_at.isoformat("T") + "Z" if latest_video else None

def fetch_latest_videos(session: Session):
    '''
    Fetch lastest video details published in the last 30.
    Queries the APIKeys thereby updating their validation.
    '''
    api_keys = session.query(APIKey).filter_by(validated=True).all()
    # published_after the latest video in the database to avoid duplicates
    published_after = get_latest_published_time(session)
    # Check all the keys
    for key_entry in api_keys:
        params = {
            'part': ','.join(VIDEO_FIELDS),
            'q': SEARCH_QUERY,
            'type': 'video',
            'order': 'date',
            'maxResults': 50,
            'key': key_entry.key
        }
        # Only add publishedAfter if it exists
        if published_after:
            params['publishedAfter'] = published_after

        response = requests.get(SEARCH_URL, params=params)
        if response.status_code == 200:
            # If a key is valid, the response is returned and the loop breaks
            logger.info(f"Fetched videos using API key: {key_entry.key}")
            return response.json().get('items', [])
        elif response.status_code == 403:
            # If a key isn't valid, the validated field of the API key is set to False in the database
            logger.warning(f"Quota exceeded or forbidden for API key: {key_entry.key}, marking as invalid.")
            key_entry.validated = False
            session.commit()
    logger.error("All API keys failed.")
    return []


def save_videos_to_db(session: Session, videos_data):
    '''
        Stores videos into the MySQL database.
    '''
    for item in videos_data:
        video_id = item['id']['videoId']
        snippet = item['snippet']

        # New Video entry with ignoring duplicates
        video = insert(Video).values(
            id=video_id,
            title=snippet['title'],
            description=snippet['description'],
            published_at=datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
            thumbnail_url=snippet['thumbnails']['high']['url'],
            channel_title=snippet['channelTitle']
        ).prefix_with("IGNORE")
        session.execute(video)
        logger.info(f"Saved new video to DB: {video_id}")
    session.commit()

def get_paginated_videos(session: Session, page: int, per_page: int):
    '''
        Return paginated records sorted by publishing date.
    '''
    offset = (page - 1) * per_page
    videos = session.query(Video).order_by(Video.published_at.desc()).offset(offset).limit(per_page).all()
    return [
        {
            'id': v.id,
            'title': v.title,
            'description': v.description,
            'published_at': v.published_at.isoformat(),
            'thumbnail_url': v.thumbnail_url,
            'channel_title': v.channel_title
        } for v in videos
    ]

def add_api_key(session: Session, key: str):
    '''
        Add new API Key to the database.
    '''
    # Checking if already present
    existing = session.query(APIKey).filter_by(key=key).first()
    if existing:
        return "API key already exists", 200
    key_entry = APIKey(key=key, validated=True)
    session.add(key_entry)
    session.commit()
    return "API key added successfully", 201

def get_all_videos(session: Session):
    """
    Returns a list of all videos from the database.
    """
    videos = session.query(Video).order_by(Video.published_at.desc()).all()
    return [{
        'id': v.id,
        'title': v.title,
        'description': v.description,
        'published_at': v.published_at.isoformat(),
        'thumbnail_url': v.thumbnail_url
    } for v in videos]

def get_videos_by_title(session, search_string):
    """
    Returns all videos whose titles partially match the given search string(case-insensitive).
    """
    search_pattern = f"%{search_string}%"
    # Querying the database according to the search pattern
    videos = session.query(Video).filter(
        Video.title.ilike(search_pattern)
    ).order_by(Video.published_at.desc()).all()

    return [{
        'id': v.id,
        'title': v.title,
        'description': v.description,
        'published_at': v.published_at.isoformat(),
        'thumbnail_url': v.thumbnail_url
    } for v in videos]
