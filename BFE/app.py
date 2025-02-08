from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from scraper import scrape_dog_food
import pandas as pd
import os
from datetime import datetime


# render trial
# PostgreSQL database URL
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///bfe.db")
# (hid this so flask can connect) DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bfe.db")  # Fallback to SQLite locally
#app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app = Flask(__name__)

#railway trial
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bfe.db")  # Uses SQLite locally
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# SQLite Configure database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bfe.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

## Define Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False)  # Walk, Feed, Custom
    scheduled_time = db.Column(db.DateTime, nullable=False)  # For preset tasks
    completed = db.Column(db.Boolean, default=False)
    custom_task_name = db.Column(db.String(100), nullable=True)  # For custom tasks
    notes = db.Column(db.Text, nullable=True)  # Notes when marking complete
    image_filename = db.Column(db.String(255), nullable=True)  # Image file path
    
#Create Predefined Daily Tasks
from datetime import datetime, timedelta

def create_daily_tasks():
    today = datetime.today().date()

    # Check if tasks already exist for today
    existing_tasks = Task.query.filter(Task.scheduled_time >= today).all()
    if existing_tasks:
        return  # Avoid duplicate tasks

    # Define daily walks and feeding times
    daily_tasks = [
        ("Walk", datetime.combine(today, datetime.strptime("07:00", "%H:%M").time())),
        ("Walk", datetime.combine(today, datetime.strptime("12:00", "%H:%M").time())),
        ("Walk", datetime.combine(today, datetime.strptime("18:00", "%H:%M").time())),
        ("Walk", datetime.combine(today, datetime.strptime("22:00", "%H:%M").time())),
        ("Feed", datetime.combine(today, datetime.strptime("08:00", "%H:%M").time())),
        ("Feed", datetime.combine(today, datetime.strptime("19:00", "%H:%M").time()))
    ]

    # Add tasks to the database
    for task_type, time in daily_tasks:
        new_task = Task(task_type=task_type, scheduled_time=time)
        db.session.add(new_task)

    db.session.commit()

#Ensure Tasks Are Created Daily
with app.app_context():
    db.create_all()
    create_daily_tasks()  # Ensure daily tasks are generated


# Home route to display tasks
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        task_name = request.form['task_name']
        new_task = Task(task_name=task_name)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# Route to mark tasks as completed
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
    return redirect(url_for('home'))

# Route to export tasks to CSV
@app.route('/export')
def export_tasks():
    tasks = Task.query.all()

    # Convert to DataFrame
    df = pd.DataFrame([(task.id, task.task_name, task.completed) for task in tasks], 
                      columns=['Task ID', 'Task Name', 'Completed'])

    # Save to CSV
    file_path = "task_report.csv"
    df.to_csv(file_path, index=False)

    # Send the file to the user
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))




