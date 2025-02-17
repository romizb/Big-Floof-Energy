from flask_sqlalchemy import SQLAlchemy
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from app import db
from sqlalchemy import text

# Initialize Flask App (only if running as standalone)
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bfe.db"
#db = SQLAlchemy(app)

# Database Configuration (SQLite Locally, PostgreSQL for Railway)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:JpEcVVcazObHteBNTKKcGuOAPjDJVjQU@postgres.railway.internal:5432/railway")  # Default for local dev
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL



# for using using SQLAlchemy (so can work on railway)
def initialize_news_table():
    with db.engine.connect() as connection:
        connection.execute(text('''
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        connection.commit()

# Call this function before fetching news
initialize_news_table()


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
        db.create_all()
    fetch_dog_news()
