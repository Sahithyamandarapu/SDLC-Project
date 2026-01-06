from flask import Flask, render_template, request, redirect, flash
import sqlite3
import logging
import os

app = Flask(__name__)
app.config['DATABASE'] = 'todo.db'
app.secret_key = 'your-secret-key'

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table if it doesn't exist (without due_date initially)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check if 'due_date' column exists
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'due_date' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        print("Added 'due_date' column to tasks table.")

    conn.commit()
    conn.close()

init_db()

# Home route - Display tasks
@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Add Task
@app.route('/add', methods=['POST'])
def add_task():
    try:
        title = request.form['title']
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Pending')
        due_date = request.form.get('due_date', '')

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO tasks (title, description, priority, status, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, priority, status, due_date))
        conn.commit()
        conn.close()

        flash('Task added successfully!', 'success')
        logger.info(f'Task added: {title}')
    except Exception as e:
        flash(f'Error adding task: {str(e)}', 'error')
        logger.error(f'Error adding task: {str(e)}')
    return redirect('/')

# Delete Task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        flash('Task deleted!', 'success')
        logger.info(f'Task deleted: {task_id}')
    except Exception as e:
        flash(f'Error deleting task: {str(e)}', 'error')
        logger.error(f'Error deleting task: {str(e)}')
    return redirect('/')

# Edit Task - Form
@app.route('/edit/<int:task_id>')
def edit_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    if task is None:
        flash('Task not found!', 'error')
        return redirect('/')
    return render_template('edit_task.html', task=task)

# Update Task
@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    try:
        title = request.form['title']
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Pending')
        due_date = request.form.get('due_date', '')

        conn = get_db_connection()
        conn.execute('''
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, status = ?, due_date = ?
            WHERE id = ?
        ''', (title, description, priority, status, due_date, task_id))
        conn.commit()
        conn.close()

        flash('Task updated successfully!', 'success')
        logger.info(f'Task updated: {task_id}')
    except Exception as e:
        flash(f'Error updating task: {str(e)}', 'error')
        logger.error(f'Error updating task: {str(e)}')
    return redirect('/')

# Run app
if __name__ == '__main__':
    app.run(debug=True)
