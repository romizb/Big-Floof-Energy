import feedparser
import requests
import random
import time


#to minimize slowdown of the program, scraping accurs every 30 min instead of every reload :)
cached_news = None
last_scraped_time = 0

def fetch_dog_news():
    global cached_news, last_scraped_time

    # Refresh news every 30 minutes (1800 seconds)
    if cached_news and time.time() - last_scraped_time < 1800:
        return cached_news  # Return cached data if recent

    print("Fetching fresh dog news...")  # Debugging

    feed_urls = [
        "http://www.dogster.com/feed",
        "http://www.dogtipper.com/feed",
        "http://www.companionanimalpsychology.com/feeds/posts/default?alt=rss",
        "https://thedailycorgi.com/feed",
        "https://www.avma.org/news/rss-feeds"
    ]

    news_items = []

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # Get only the first 3 articles
            
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                
            })

    # Sort news items by published date, most recent first
    news_items.sort(key=lambda x: x['published'], reverse=True)
    cached_news = news_items[:3]  # Store in cache
    last_scraped_time = time.time()  # Update last scraped time

    return cached_news









