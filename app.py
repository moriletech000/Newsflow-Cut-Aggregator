from flask import Flask, render_template, jsonify, request
from flask_caching import Cache
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import scrape_all_sources, get_source_names, get_countries, get_regions
from datetime import datetime
import atexit

app = Flask(__name__)

# Configure caching
cache_config = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 600  # 10 minutes
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Global variable to track last update
last_update_time = None
scrape_error = False

def fetch_and_cache_articles():
    """Fetch articles and update cache"""
    global last_update_time, scrape_error
    
    try:
        print(f"Fetching articles at {datetime.now()}")
        articles = scrape_all_sources()
        cache.set('articles', articles)
        last_update_time = datetime.now()
        scrape_error = False
        print(f"Cached {len(articles)} articles")
        return articles
    except Exception as e:
        print(f"Error fetching articles: {str(e)}")
        scrape_error = True
        # Return cached articles if available
        return cache.get('articles') or []

@cache.memoize(timeout=600)
def get_articles():
    """Get articles from cache or fetch if not available"""
    articles = cache.get('articles')
    if articles is None:
        articles = fetch_and_cache_articles()
    return articles

@app.route('/')
def index():
    """Render main page"""
    articles = get_articles()
    sources = get_source_names()
    countries = get_countries()
    regions = get_regions()
    
    return render_template(
        'index.html',
        articles=articles,
        sources=sources,
        countries=countries,
        regions=regions,
        last_update=last_update_time,
        has_error=scrape_error
    )

@app.route('/api/news')
def api_news():
    """API endpoint to get filtered news articles"""
    articles = get_articles()
    
    # Get query parameters
    source_filter = request.args.get('source', '').strip()
    category_filter = request.args.get('category', '').strip()
    country_filter = request.args.get('country', '').strip()
    region_filter = request.args.get('region', '').strip()
    search_query = request.args.get('q', '').strip().lower()
    
    # Apply filters
    filtered_articles = articles
    
    if source_filter and source_filter != 'All':
        filtered_articles = [a for a in filtered_articles if a['source'] == source_filter]
    
    if category_filter and category_filter != 'All':
        filtered_articles = [a for a in filtered_articles if a['category'] == category_filter]
    
    if country_filter and country_filter != 'All':
        filtered_articles = [a for a in filtered_articles if a.get('country') == country_filter]
    
    if region_filter and region_filter != 'All':
        filtered_articles = [a for a in filtered_articles if a.get('region') == region_filter]
    
    if search_query:
        filtered_articles = [
            a for a in filtered_articles 
            if search_query in a['title'].lower() or search_query in a['summary'].lower()
        ]
    
    return jsonify({
        'articles': filtered_articles,
        'count': len(filtered_articles),
        'last_update': last_update_time.isoformat() if last_update_time else None,
        'has_error': scrape_error
    })

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh articles"""
    cache.clear()
    articles = fetch_and_cache_articles()
    
    return jsonify({
        'success': True,
        'count': len(articles),
        'last_update': last_update_time.isoformat() if last_update_time else None,
        'has_error': scrape_error
    })

# Initialize scheduler for background updates
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_cache_articles, trigger="interval", minutes=15)
scheduler.start()

# Fetch articles on startup
with app.app_context():
    fetch_and_cache_articles()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
