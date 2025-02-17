import unittest
from app import app, db, User, Task
from scraper import fetch_dog_news
from datetime import datetime
from flask import session

class BFETestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Runs once before all tests. Initializes test app. """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Use in-memory DB
        cls.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            cls.add_test_users()
            cls.create_test_tasks()

    @classmethod
    def tearDownClass(cls):
        """ Runs once after all tests. Cleans up the database. """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    @classmethod
    def add_test_users(cls):
        """ Adds test users to the database, avoiding duplicates """
        test_users = ["romi", "mika", "tamar", "stranger"]
        for username in test_users:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:  # Only add if the user doesn't exist
                db.session.add(User(username=username))
        db.session.commit()


    @classmethod
    def create_test_tasks(cls):
        """ Creates sample tasks for testing """
        today = datetime.today().date()
        tasks = [
            Task(task_type="Walk (Morning)", task_date=today),
            Task(task_type="Feed (Evening)", task_date=today)
        ]
        db.session.bulk_save_objects(tasks)
        db.session.commit()

    def test_login_valid_user(self):
        """ Test login with a valid predefined user """
        response = self.client.post('/login', data={'username': 'romi'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('username'), 'romi')

    def test_login_invalid_user(self):
        """ Test login with an invalid username """
        response = self.client.post('/login', data={'username': 'invaliduser'}, follow_redirects=True)
        self.assertIn(b'Invalid username.', response.data)  # Ensure the error message is in the response


    def test_daily_task_creation(self):
        """ Verify that daily tasks exist """
        with app.app_context():
            today = datetime.today().date()
            tasks = Task.query.filter_by(task_date=today).all()
            self.assertGreaterEqual(len(tasks), 2)  # At least 2 test tasks

    def test_task_completion_toggle(self):
        """ Verify marking a task as completed/uncompleted """
        with app.app_context():
            task = Task.query.first()
            initial_status = task.completed
            self.client.post(f'/complete_task/{task.id}', data={'notes': 'Test note'}, follow_redirects=True)
            
            updated_task = db.session.get(Task, task.id)
            self.assertNotEqual(initial_status, updated_task.completed)  # Should be toggled

    def test_add_custom_task(self):
        """ Test adding a custom task """
        response = self.client.post('/add_task', data={'task_name': 'Buy dog treats', 'task_date': datetime.today().strftime('%Y-%m-%d')}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            task = Task.query.filter_by(custom_task_name="Buy dog treats").first()
            self.assertIsNotNone(task)

    def test_news_scraping(self):
        """ Check that dog news scraper returns valid results """
        news = fetch_dog_news()
        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        self.assertIn('title', news[0])
        self.assertIn('link', news[0])

if __name__ == '__main__':
    unittest.main()
