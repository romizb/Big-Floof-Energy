from flask_sqlalchemy import SQLAlchemy
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from sqlalchemy import text
import os 

# Initialize Flask App
app = Flask(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:JpEcVVcazObHteBNTKKcGuOAPjDJVjQU@postgres.railway.internal:5432/railway")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

# Ensure news table is correctly structured
def initialize_news_table():
    with app.app_context():
        with db.engine.connect() as connection:
            connection.execute(text('''
                DROP TABLE IF EXISTS news;
                CREATE TABLE news (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    published TEXT NOT NULL
                );
            '''))
            connection.commit()

initialize_news_table()  # Ensures table exists before inserting news

# Define the News model
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(512), nullable=False)
    published = db.Column(db.String(100), nullable=False)

# Create scheduler instance
scheduler = BackgroundScheduler()

def fetch_dog_news():
    """ Scrape dog news and store it in the database """
    feed_urls = [
        "http://www.dogster.com/feed",
        "http://www.dogtipper.com/feed",
        "http://www.companionanimalpsychology.com/feeds/posts/default?alt=rss",
        "https://thedailycorgi.com/feed",
        "https://www.avma.org/news/rss-feeds"
    ]

    with app.app_context():
        db.session.query(News).delete()  # Clear old news
        for url in feed_urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # Get top 3 articles
                news_item = News(title=entry.title, link=entry.link, published=entry.published)
                db.session.add(news_item)
        db.session.commit()
        print("News updated!")

# Add the scheduled job (runs every 6 hours)
scheduler.add_job(fetch_dog_news, 'interval', hours=6)
scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        initialize_news_table()
        db.create_all()
        fetch_dog_news()
