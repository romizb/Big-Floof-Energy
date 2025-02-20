from flask import Flask, render_template, request, redirect, url_for, send_file, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import func
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text
from scraper import start_scheduler
from collections import OrderedDict



# Initialize Flask app
app = Flask(__name__)

# ✅ Set SECRET_KEY to enable session functionality
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "0d466da06002ec41181e7206f1820bc556686281afbf6bd018e5f6dbbc235c7c")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:JpEcVVcazObHteBNTKKcGuOAPjDJVjQU@postgres.railway.internal:5432/railway")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Initialize Database
db = SQLAlchemy(app)

# Import fetch_dog_news AFTER initializing db
with app.app_context():
    from scraper import fetch_dog_news



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


# -------------------------
#new tasks are automatically created every day
#--------------------------
def add_daily_tasks():
    """ Ensure that both today's and tomorrow's tasks are preloaded without duplication. """
    with app.app_context():
        today = datetime.today().date()
        
        required_tasks = {
            "Walk (Morning)", "Walk (Afternoon)", "Walk (Evening)", "Walk (Before Bed)",
            "Feed (Morning)", "Feed (Evening)"
        }

        # Function to check and add missing tasks for a given date
        def ensure_tasks_for_date(task_date):
            existing_tasks = {task.task_type for task in Task.query.filter_by(task_date=task_date).all()}
            missing_tasks = required_tasks - existing_tasks

            if missing_tasks:
                for task_type in missing_tasks:
                    db.session.add(Task(task_type=task_type, task_date=task_date))
                db.session.commit()
                print(f"Added missing tasks for {task_date}: {missing_tasks}")

        # Ensure tasks exist for today 
        ensure_tasks_for_date(today)
        


# Run scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(add_daily_tasks, 'cron', minute=0)  # Runs every hour on the hour
scheduler.start()

#--------------------------

with app.app_context():
    db.create_all()
    add_predefined_users()
    add_daily_tasks()  # Ensure tomorrow’s tasks are also preloaded


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
        
        # Ensure error message is properly passed to the template
        return render_template('login.html', error="Invalid username.")  

    return render_template('login.html')




# -------------------------
# Log out
# -------------------------

@app.route('/logout')
def logout():
    """Logs out the user by clearing the session and redirecting to login"""
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('login'))


# -------------------------
# MAIN ROUTE - TASK & NEWS DISPLAY
# -------------------------

@app.route('/', methods=['GET', 'POST'])
def home():
    """ Displays daily tasks and latest dog news """
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    
    # Fetch all tasks grouped by date
    all_tasks = Task.query.order_by(Task.task_date).all()
    
    # Filter out past days where ALL tasks are completed, so not to bombard the user
    filtered_tasks = []
    task_status_by_date = {}
    
    for task in all_tasks:
        if task.task_date < datetime.today().date():  # Only consider past days
            if task.task_date not in task_status_by_date:
                task_status_by_date[task.task_date] = []
    
            task_status_by_date[task.task_date].append(task.completed)
    
        else:  
            # Always include today's and future tasks
            filtered_tasks.append(task)
    
    # remove fully completed past days
    for date, statuses in task_status_by_date.items():
        if not all(statuses):  # If ANY task is not completed, keep the date
            filtered_tasks.extend([t for t in all_tasks if t.task_date == date])
    
    # Sort the filtered tasks by date
    tasks = sorted(filtered_tasks, key=lambda t: t.task_date)

    grouped_tasks = OrderedDict()
    
    for task in tasks:
        task_date_key = task.task_date.strftime('%A, %B %d, %Y')  # Readable format
        if task_date_key not in grouped_tasks:
            grouped_tasks[task_date_key] = {"Walk": [], "Feed": [], "Custom": []}
    
        task_data = {
            "id": task.id,
            "task_type": task.custom_task_name if task.task_type == "Custom" else task.task_type,
            "task_date": task.task_date.strftime('%Y-%m-%d'),
            "completed": task.completed,
            "notes": task.notes,
            "completed_by": task.completed_by
        }
    
        task_category = task.task_type.split()[0]  # Identify category (Walk, Feed, Custom)
        grouped_tasks[task_date_key][task_category].append(task_data)
    
    # Ensure dates are sorted before passing to the template
    grouped_tasks = OrderedDict(sorted(grouped_tasks.items(), key=lambda x: datetime.strptime(x[0], '%A, %B %d, %Y')))


    # Get latest dog news
    with app.app_context():
        # Ensure fetch_dog_news() is executed
        fetch_dog_news()
        dog_news = db.session.execute(text("SELECT title, link FROM news ORDER BY id DESC LIMIT 3")).fetchall()
    
    # Convert fetched news into a list of dictionaries
    dog_news = [{"title": row[0], "link": row[1]} for row in dog_news] if dog_news else []


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

@app.route("/add_task", methods=["POST"])
def add_task():
    if request.method == "POST":
        task_name = request.form.get("task_name")  # User input for task name
        task_due_date = request.form.get("task_due_date")  # Fetch task date from form

        # If no date is provided, use today's date
        if not task_due_date:
            task_due_date = datetime.today().strftime('%Y-%m-%d')

        # Convert task_due_date to date format
        task_date = datetime.strptime(task_due_date, '%Y-%m-%d').date()

        # Create new task as a custom task
        new_task = Task(
            task_type="Custom",  # Ensuring it's marked as a custom task
            custom_task_name=task_name,  # Save user input in the correct column
            task_date=task_date,
            completed=False
        )

        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for("home"))

# -------------------------
#Start the Scheduler on Launch
# -------------------------
with app.app_context():
    start_scheduler()

# -------------------------
# START THE FLASK APP
# -------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
