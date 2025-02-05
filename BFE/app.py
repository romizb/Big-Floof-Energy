from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from scraper import scrape_dog_food
import pandas as pd
import os




app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bfe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

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
    app.run(debug=True)

