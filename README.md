# YouTube Video Fetcher

This project is a Flask-based server that continuously fetches the latest YouTube videos for a search query, stores them in a SQLite database, along with an API to retrieve the data in a paginated format.

A simple dashboard (via `index.html`) allows you to view and search videos by keywords directly from the browser.

---

## Features Implemented

### Basic Requirements
- **Periodic YouTube Data Fetching:** The server runs a background thread that calls the YouTube API every 10 seconds using the most recently validated API key. It stores new videos in the SQLite DB.
- **Video Storage:** It saves the title, description, published date, thumbnail URL, and channel title with proper indexing.
- **Paginated GET API:** An endpoint `/videos` returns the stored video list sorted by published datetime in descending order.

### Optimization & Scalability
- Videos are only saved if they aren’t already in the database.
- SQLAlchemy is used for ORM, ensuring better DB management and cleaner abstractions.
- Logs are recorded for video insertion and key failures.

---

## Bonus Features

- **Multiple API Keys Support:** You can supply multiple API keys. If a quota is exhausted, the system automatically switches to the next available key.
- **API Key Management Endpoint:** Use `/api-keys` to add new API keys dynamically via a POST request.
- **Dashboard (Optional UI):** A lightweight HTML page (`index.html`) lets you search and view stored videos using a keyword search and default load.

![Dashboard](https://drive.google.com/file/d/1O5D7B2-ZHR-18RjdrCR1Euw-02Srv_ed/view?usp=sharing)
---

## How to Run

### 1. Clone and install dependencies
```bash
git clone https://github.com/Ratul-Saha-003/Fam-Backend-Assignment.git
cd into the project
pip install -r requirements.txt
```

### 2. Setup the env
```bash
INTERVAL= <interval in which youtube API is fetched>
DATABASE_URI= <url of sqlite db>
SEARCH_QUERY = <search query>
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
```

### 3. Run the server
```bash
python app.py
```

## API Endpoints

### 1. Add a New API Key
POST /api-keys
Content-Type: application/json
Body: 
{
  "key": "API_KEY_HERE"
}

![API response](https://drive.google.com/file/d/1FHisdl6fwx5BoejMZpAx0yM4MrcQpvWL/view?usp=sharing)

### 2. Fetch paginated videos
GET /videos?page=1&per_page=10

![API response](https://drive.google.com/file/d/1yRl07inHIl-y3HcOg-zNbWMMF_aLj5FF/view?usp=sharing)
