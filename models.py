from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Video model to store YouTubevideo details
class Video(Base):
    __tablename__ = 'videos'

    # Required columns for Video model
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    published_at = Column(DateTime)
    thumbnail_url = Column(String)
    channel_title = Column(String)
    
    def __repr__(self):
        return f"<Video(id={self.id}, title={self.title})>"
    

# APIKey model to store and manage multiple YouTube API keys
class APIKey(Base):
    __tablename__ = 'api_keys'

    # Required columns for APIKey model
    key = Column(String, primary_key=True)
    validated = Column(Boolean, default=True)