from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from datetime import datetime
from flask import jsonify
from scraper import fetch_dog_news
from sqlalchemy.sql.expression import func

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for user sessions

# Database Configuration (SQLite Locally, PostgreSQL for Railway)
if os.getenv("RAILWAY_ENV"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bfe.db"  

db = SQLAlchemy(app)

# -------------------------
# DATABASE MODELS
# -------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False)  # Walk, Feed, Custom
    task_date = db.Column(db.Date, nullable=False)  
    completed = db.Column(db.Boolean, default=False)
    custom_task_name = db.Column(db.String(100), nullable=True)  
    notes = db.Column(db.Text, nullable=True)  
    completed_by = db.Column(db.String(50), nullable=True)  

# -------------------------
# SETUP: PREDEFINED USERS & DAILY TASKS
# -------------------------

def add_predefined_users():
    """ Adds predefined usernames to the database """
    predefined_users = ["romi", "mika", "tamar", "stranger"]  # Store in lowercase
    for username in predefined_users:
        user = User.query.filter(func.lower(User.username) == username).first()
        if not user:
            db.session.add(User(username=username))
    db.session.commit()

def create_daily_tasks():
    """ Ensures that predefined daily tasks exist """
    today = datetime.today().date()
    if Task.query.filter_by(task_date=today).first():
        return  # Avoid duplicates

    daily_tasks = [
        ("Walk (Morning)", today),
        ("Walk (Afternoon)", today),
        ("Walk (Evening)", today),
        ("Walk (Before Bed)", today),
        ("Feed (Morning)", today),
        ("Feed (Evening)", today)
    ]

    for task_type, date in daily_tasks:
        db.session.add(Task(task_type=task_type, task_date=date))

    db.session.commit()

with app.app_context():
    db.create_all()
    add_predefined_users()
    create_daily_tasks()

# -------------------------
# USER AUTHENTICATION
# -------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Handles user login by checking predefined usernames """
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        user = User.query.filter(func.lower(User.username) == username).first()
        if user:
            session['username'] = user.username
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid username.")
    return render_template('login.html')

# -------------------------
# MAIN ROUTE - TASK & NEWS DISPLAY
# -------------------------

@app.route('/', methods=['GET', 'POST'])
def home():
    """ Displays daily tasks and latest dog news """
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    
    # Retrieve tasks grouped by date
    tasks = Task.query.all()
    grouped_tasks = {}

    for task in tasks:
        task_date = task.task_date.strftime('%A, %B %d, %Y')
        if task_date not in grouped_tasks:
            grouped_tasks[task_date] = {"Walk": [], "Feed": [], "Custom": []}
        
        task_data = {
            "id": task.id,
            "task_type": task.task_type,
            "task_date": task.task_date.strftime('%Y-%m-%d'),
            "completed": task.completed,
            "custom_task_name": task.custom_task_name,
            "notes": task.notes,
            "completed_by": task.completed_by
        }

        grouped_tasks[task_date][task.task_type.split()[0]].append(task_data)

    # Get latest dog news
    dog_news = fetch_dog_news()

    return render_template('index.html', grouped_tasks=grouped_tasks, username=username, dog_news=dog_news)


# -------------------------
# TASK COMPLETION & NOTES
# -------------------------

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    """ Marks a task as completed/uncompleted and saves user notes """
    if 'username' not in session:
        return redirect(url_for('login'))

    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed  
        task.notes = request.form.get('notes', '') if task.completed else None  
        task.completed_by = session['username'] if task.completed else None  
        db.session.commit()
    return redirect(url_for('home'))

# -------------------------
# TASK EXPORT TO CSV
# -------------------------

@app.route('/export')
def export_tasks():
    """ Exports task data to a CSV file """
    tasks = Task.query.all()
    df = pd.DataFrame([(t.id, t.custom_task_name or t.task_type, t.task_date, t.completed, t.notes, t.completed_by) for t in tasks], 
                      columns=['Task ID', 'Task Name', 'Task Date', 'Completed', 'Notes', 'Completed By'])

    file_path = "task_report.csv"
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)

# -------------------------
# CUSTOM TASK CREATION
# -------------------------

@app.route('/add_task', methods=['POST'])
def add_task():
    """ Allows users to create custom tasks """
    task_name = request.form['task_name']
    task_date = request.form['task_date']  
    if task_name and task_date:
        db.session.add(Task(task_type="Custom", task_date=datetime.strptime(task_date, "%Y-%m-%d"), custom_task_name=task_name))
        db.session.commit()
    return redirect(url_for('home'))

# -------------------------
# START THE FLASK APP
# -------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
