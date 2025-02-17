import pytest
from bfe.app import app, db, User, Task
from datetime import datetime
import os
from bfe.scraper import fetch_dog_news

# -------------------------
# CONFIGURE TESTING DATABASE
# -------------------------

@pytest.fixture
def client():
    """ Setup a test client and an isolated database """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"  # Use a test DB
    client = app.test_client()

    with app.app_context():
        db.create_all()  # Setup the database for tests
        db.session.add(User(username="test_user"))
        db.session.commit()
    
    yield client  

    # Cleanup after tests
    with app.app_context():
        db.drop_all()

# -------------------------
# AUTHENTICATION TESTS
# -------------------------

def test_valid_login(client):
    """ Test login with a valid user """
    response = client.post('/login', data={'username': 'test_user'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Check if login success message is shown

def test_invalid_login(client):
    """ Test login with an invalid user """
    response = client.post('/login', data={'username': 'fake_user'}, follow_redirects=True)
    assert b"Invalid username" in response.data  # Should display invalid login message

# -------------------------
# TASK MANAGEMENT TESTS
# -------------------------

def test_create_task(client):
    """ Test adding a new custom task """
    response = client.post('/add_task', data={'task_name': 'Vet Appointment', 'task_date': '2025-02-28'}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        task = Task.query.filter_by(custom_task_name='Vet Appointment').first()
        assert task is not None

def test_complete_task(client):
    """ Test marking a task as completed """
    with app.app_context():
        task = Task(task_type="Custom", task_date=datetime.today().date(), custom_task_name="Test Task")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post(f'/complete_task/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        task = Task.query.get(task_id)
        assert task.completed == True  # Task should be marked as completed

# -------------------------
# WEB SCRAPING TEST
# -------------------------

def test_web_scraping():
    """ Test the web scraping function does not return empty data """
    news = fetch_dog_news()
    assert len(news) > 0  # Ensure at least one news article is retrieved

# -------------------------
# EXPORT FUNCTION TEST
# -------------------------

def test_export_tasks(client):
    """ Test CSV export function """
    response = client.get('/export')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'  # Ensure response is a CSV file
