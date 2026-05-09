import feedparser
import requests
from datetime import datetime
from dateutil import parser as date_parser
import re
from difflib import SequenceMatcher

# Global news sources organized by country/region
NEWS_SOURCES = {
    # United States
    'CNN (USA)': {
        'url': 'http://rss.cnn.com/rss/cnn_topstories.rss',
        'country': 'United States',
        'region': 'North America'
    },
    'NPR (USA)': {
        'url': 'https://feeds.npr.org/1001/rss.xml',
        'country': 'United States',
        'region': 'North America'
    },
    'New York Times (USA)': {
        'url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        'country': 'United States',
        'region': 'North America'
    },
    
    # United Kingdom
    'BBC (UK)': {
        'url': 'http://feeds.bbci.co.uk/news/rss.xml',
        'country': 'United Kingdom',
        'region': 'Europe'
    },
    'The Guardian (UK)': {
        'url': 'https://www.theguardian.com/world/rss',
        'country': 'United Kingdom',
        'region': 'Europe'
    },
    'Reuters (UK)': {
        'url': 'https://feeds.reuters.com/reuters/topNews',
        'country': 'United Kingdom',
        'region': 'Europe'
    },
    
    # Canada
    'CBC (Canada)': {
        'url': 'https://www.cbc.ca/cmlink/rss-topstories',
        'country': 'Canada',
        'region': 'North America'
    },
    
    # Australia
    'ABC News (Australia)': {
        'url': 'https://www.abc.net.au/news/feed/51120/rss.xml',
        'country': 'Australia',
        'region': 'Oceania'
    },
    
    # Germany
    'Deutsche Welle (Germany)': {
        'url': 'https://rss.dw.com/xml/rss-en-all',
        'country': 'Germany',
        'region': 'Europe'
    },
    
    # France
    'France 24 (France)': {
        'url': 'https://www.france24.com/en/rss',
        'country': 'France',
        'region': 'Europe'
    },
    
    # Middle East
    'Al Jazeera (Qatar)': {
        'url': 'https://www.aljazeera.com/xml/rss/all.xml',
        'country': 'Qatar',
        'region': 'Middle East'
    },
    
    # India
    'Times of India (India)': {
        'url': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'country': 'India',
        'region': 'Asia'
    },
    
    # Japan
    'Japan Times (Japan)': {
        'url': 'https://www.japantimes.co.jp/feed/',
        'country': 'Japan',
        'region': 'Asia'
    },
    
    # China
    'China Daily (China)': {
        'url': 'http://www.chinadaily.com.cn/rss/world_rss.xml',
        'country': 'China',
        'region': 'Asia'
    },
    
    # Russia
    'RT (Russia)': {
        'url': 'https://www.rt.com/rss/',
        'country': 'Russia',
        'region': 'Europe/Asia'
    },
    
    # South Africa
    'News24 (South Africa)': {
        'url': 'https://feeds.news24.com/articles/news24/TopStories/rss',
        'country': 'South Africa',
        'region': 'Africa'
    },
    
    # Brazil
    'Folha (Brazil)': {
        'url': 'https://feeds.folha.uol.com.br/mundo/rss091.xml',
        'country': 'Brazil',
        'region': 'South America'
    },
    
    # Mexico
    'El Universal (Mexico)': {
        'url': 'https://www.eluniversal.com.mx/rss.xml',
        'country': 'Mexico',
        'region': 'North America'
    },
    
    # Argentina
    'La Nacion (Argentina)': {
        'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/',
        'country': 'Argentina',
        'region': 'South America'
    },
    
    # Tech News (Global)
    'Ars Technica (Global)': {
        'url': 'http://feeds.arstechnica.com/arstechnica/index',
        'country': 'Global',
        'region': 'Technology'
    },
    'TechCrunch (Global)': {
        'url': 'https://techcrunch.com/feed/',
        'country': 'Global',
        'region': 'Technology'
    }
}

def guess_category(title, summary, source, source_config):
    """Guess article category based on keywords"""
    text = (title + ' ' + summary).lower()
    
    # Check if it's a tech source
    if 'tech' in source.lower() or source_config.get('region') == 'Technology':
        return 'Tech'
    
    # Category keywords
    categories = {
        'Tech': ['technology', 'tech', 'ai', 'software', 'computer', 'digital', 'cyber', 'internet', 'app', 'smartphone'],
        'Science': ['science', 'research', 'study', 'scientist', 'space', 'climate', 'health', 'medical', 'vaccine'],
        'Politics': ['politics', 'election', 'government', 'president', 'minister', 'parliament', 'congress', 'vote', 'policy'],
        'Business': ['business', 'economy', 'market', 'stock', 'trade', 'company', 'finance', 'bank', 'dollar', 'euro'],
        'World': ['world', 'international', 'country', 'war', 'conflict', 'crisis', 'global']
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return 'World'

def similar(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate_articles(articles, threshold=0.85):
    """Remove duplicate articles based on title similarity"""
    unique_articles = []
    
    for article in articles:
        is_duplicate = False
        for unique in unique_articles:
            if similar(article['title'], unique['title']) > threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_articles.append(article)
    
    return unique_articles

def parse_date(date_string):
    """Parse date string and return formatted date"""
    try:
        if date_string:
            dt = date_parser.parse(date_string)
            return dt.strftime('%B %d, %Y at %I:%M %p')
        return 'Unknown date'
    except:
        return 'Unknown date'

def scrape_source(source_name, source_config):
    """Scrape a single news source"""
    articles = []
    
    try:
        # Set timeout and user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Parse RSS feed
        feed = feedparser.parse(source_config['url'], request_headers=headers)
        
        if not feed.entries:
            print(f"Warning: No entries found for {source_name}")
            return articles
        
        for entry in feed.entries[:20]:  # Limit to 20 articles per source
            try:
                title = entry.get('title', 'No title')
                link = entry.get('link', '#')
                
                # Get summary
                summary = entry.get('summary', entry.get('description', ''))
                # Clean HTML tags from summary
                summary = re.sub('<[^<]+?>', '', summary)
                # Truncate to 180 characters
                summary = summary[:180] + '...' if len(summary) > 180 else summary
                
                # Get published date
                published = entry.get('published', entry.get('updated', ''))
                published_formatted = parse_date(published)
                
                # Get raw timestamp for sorting
                try:
                    if published:
                        published_timestamp = date_parser.parse(published)
                        # Make timezone-naive for comparison
                        if published_timestamp.tzinfo is not None:
                            published_timestamp = published_timestamp.replace(tzinfo=None)
                    else:
                        published_timestamp = datetime.now()
                except:
                    published_timestamp = datetime.now()
                
                # Guess category
                category = guess_category(title, summary, source_name, source_config)
                
                article = {
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published': published_formatted,
                    'published_timestamp': published_timestamp,
                    'source': source_name,
                    'country': source_config.get('country', 'Unknown'),
                    'region': source_config.get('region', 'Unknown'),
                    'category': category
                }
                
                articles.append(article)
                
            except Exception as e:
                print(f"Error parsing entry from {source_name}: {str(e)}")
                continue
        
        print(f"Successfully scraped {len(articles)} articles from {source_name}")
        
    except Exception as e:
        print(f"Error scraping {source_name}: {str(e)}")
    
    return articles

def scrape_all_sources():
    """Scrape all news sources and return aggregated articles"""
    all_articles = []
    
    print("Starting news scraping...")
    
    for source_name, source_config in NEWS_SOURCES.items():
        articles = scrape_source(source_name, source_config)
        all_articles.extend(articles)
    
    # Deduplicate articles
    all_articles = deduplicate_articles(all_articles)
    
    # Sort by published date, newest first
    all_articles.sort(key=lambda x: x['published_timestamp'], reverse=True)
    
    # Remove timestamp field (used only for sorting)
    for article in all_articles:
        del article['published_timestamp']
    
    print(f"Total articles after deduplication: {len(all_articles)}")
    
    return all_articles

def get_source_names():
    """Return list of all source names"""
    return list(NEWS_SOURCES.keys())

def get_countries():
    """Return list of unique countries"""
    countries = set()
    for source_config in NEWS_SOURCES.values():
        countries.add(source_config.get('country', 'Unknown'))
    return sorted(list(countries))

def get_regions():
    """Return list of unique regions"""
    regions = set()
    for source_config in NEWS_SOURCES.values():
        regions.add(source_config.get('region', 'Unknown'))
    return sorted(list(regions))
