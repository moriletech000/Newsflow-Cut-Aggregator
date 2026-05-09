# NEWSFLOW CUT - Live News Aggregator

A stunning, editorial-grade news aggregator that scrapes live headlines from multiple trusted news sources and displays them in a dark luxury magazine aesthetic.

![NEWSFLOW](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)

## Features

 **Live News Aggregation** — Scrapes headlines from 5 major news sources in real-time  
 **Editorial Design** — Dark luxury aesthetic inspired by high-end print publications  
 **Auto-Refresh** — Background updates every 15 minutes  
 **Smart Filtering** — Filter by source, category, or search keywords  
 **Fully Responsive** — Beautiful on desktop, tablet, and mobile  
 **Fast & Cached** — 10-minute cache for optimal performance  
 **Deduplication** — Intelligent removal of duplicate articles  

## News Sources

- **BBC News** — World news and analysis
- **Reuters** — Top international headlines
- **Al Jazeera** — Global news coverage
- **NPR News** — US and world news
- **Ars Technica** — Technology and science news

## Tech Stack

**Backend:**
- Flask 3.0 — Web framework
- Flask-Caching — Response caching
- Feedparser — RSS feed parsing
- BeautifulSoup4 — HTML parsing
- APScheduler — Background job scheduling
- Requests — HTTP library

**Frontend:**
- Pure CSS — No frameworks
- Vanilla JavaScript — No jQuery
- Google Fonts — Playfair Display & Libre Baskerville
- Responsive Grid Layout

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```bash
   cd news_aggregator
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   
   Navigate to: `http://localhost:5000`

That's it! The app will automatically start scraping news sources and display them.

## Usage

### Main Interface

- **Hero Article** — The latest/top article displayed prominently
- **Filter by Source** — Click source chips to filter articles
- **Filter by Category** — Click category chips (World, Tech, Science, etc.)
- **Search** — Type keywords to search article titles and summaries
- **Refresh Feed** — Click the "Refresh Feed" button to manually update

### API Endpoints

#### Get News Articles
```
GET /api/news
```

**Query Parameters:**
- `source` — Filter by source name (e.g., `BBC`, `Reuters`)
- `category` — Filter by category (e.g., `Tech`, `World`)
- `q` — Search query string

**Example:**
```
GET /api/news?source=BBC&category=Tech&q=artificial
```

**Response:**
```json
{
  "articles": [...],
  "count": 42,
  "last_update": "2026-05-09T10:30:00",
  "has_error": false
}
```

#### Refresh Articles
```
GET /api/refresh
```

Clears cache and re-scrapes all sources.

**Response:**
```json
{
  "success": true,
  "count": 87,
  "last_update": "2026-05-09T10:35:00",
  "has_error": false
}
```

## Configuration

### Cache Settings

Edit `app.py` to modify cache timeout:

```python
cache_config = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 600  # 10 minutes (in seconds)
}
```

### Auto-Refresh Interval

Edit `app.py` to change background refresh frequency:

```python
scheduler.add_job(func=fetch_and_cache_articles, trigger="interval", minutes=15)
```

### Adding News Sources

Edit `scraper.py` to add more RSS feeds:

```python
NEWS_SOURCES = {
    'Your Source': {
        'url': 'https://example.com/rss.xml',
        'category': 'World'
    }
}
```

## Error Handling

- **Source Unavailable** — If a news source fails, the app continues with other sources
- **Cache Fallback** — If scraping fails, displays last cached data with a warning banner
- **Deduplication** — Removes duplicate articles based on title similarity (85% threshold)

## Design Philosophy

NEWSFLOW combines the gravitas of traditional print journalism with modern web interactivity:

- **Typography** — Playfair Display for headlines (editorial authority), Libre Baskerville for body text (readability)
- **Color Palette** — Deep charcoal backgrounds with cream text and electric amber accents
- **Layout** — Asymmetric editorial grid inspired by The Economist and Bloomberg
- **Interactions** — Subtle animations and hover states that feel intentional, not gimmicky

## Project Structure

```
news_aggregator/
├── app.py                 # Flask application and routes
├── scraper.py             # News scraping logic
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── static/
│   ├── style.css          # All CSS styles
│   └── app.js             # Frontend JavaScript
└── templates/
    └── index.html         # Main HTML template
```

## Performance

- **Initial Load** — ~2-3 seconds (scraping 5 sources)
- **Cached Requests** — <100ms
- **Background Updates** — Every 15 minutes
- **Articles per Source** — Limited to 20 for performance

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### "No articles found"
- Check your internet connection
- Some RSS feeds may be temporarily unavailable
- Click "Refresh Feed" to retry

### Port 5000 already in use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001, host='0.0.0.0')
```

### Dependencies installation fails
Try upgrading pip first:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## License

This project is open source and available for educational and personal use.

## Credits

Built with Flask, Feedparser, and a passion for beautiful design.

---

**NEWSFLOW** — Where news meets design.
