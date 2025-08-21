# app.py - Your Flask server
from flask import Flask, request, jsonify, render_template_string, send_from_directory
import mysql.connector
from mysql.connector import Error  

# Create the Flask app
app = Flask(__name__)

# Favicon link to app.py
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

# NEW addition: MySQL connection settings 
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MYSQLabid-010',
    'database': 'task_manager'
}

# NEW: Connect to MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print("Database connection failed:", e)
        return None

# NEW: Create table if not exists
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text VARCHAR(255) NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

# HTML template (you already had this — good!)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>📝 My Task Manager</title>
    <style>
      body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; background-color: #f5f5f5; }
      h1 { text-align: center; color: #333; margin-bottom: 30px; }
      .input-section { display: flex; gap: 10px; margin-bottom: 20px; }
      #taskInput { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
      button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
      button:hover { background-color: #0056b3; }
      .task-item { display: flex; align-items: center; padding: 10px; margin: 5px 0; background: #fff; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
      .task-item input[type="checkbox"] { margin-right: 10px; }
      .task-text { flex: 1; margin-right: 10px; }
      .delete-btn { background-color: #dc3545; padding: 5px 10px; font-size: 12px; }
      .delete-btn:hover { background-color: #c82333; }
      .completed { text-decoration: line-through; opacity: .6; }
      .no-tasks { text-align: center; color: #666; font-style: italic; padding: 40px 20px; background: #fff; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
    </style>
  </head>
  <body>
    <h1>📝 My Task Manager</h1>

    <div class="input-section">
      <input type="text" id="taskInput" placeholder="What do you need to do?" />
      <button onclick="addTask()">Add Task</button>
    </div>

    <div id="taskList"></div>

    <script>
      document.addEventListener('DOMContentLoaded', function () {
        loadTasks();
        document.getElementById('taskInput').addEventListener('keypress', function (e) {
          if (e.key === 'Enter') addTask();
        });
      });

      async function loadTasks() {
        try {
          const res = await fetch('/api/tasks');
          const tasks = await res.json();
          displayTasks(tasks);
        } catch (err) {
          console.error('Error loading tasks:', err);
          document.getElementById('taskList').innerHTML = '<div class="no-tasks">Error loading tasks</div>';
        }
      }

      async function addTask() {
        const input = document.getElementById('taskInput');
        const text = input.value.trim();
        if (!text) { alert('Please enter a task!'); return; }

        try {
          const res = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
          });
          if (!res.ok) { alert('Error adding task'); return; }
          input.value = '';
          loadTasks();
        } catch (err) {
          console.error('Error adding task:', err);
          alert('Error adding task');
        }
      }

      function displayTasks(tasks) {
        const list = document.getElementById('taskList');
        if (!tasks || tasks.length === 0) {
          list.innerHTML = '<div class="no-tasks">🎯 No tasks yet! Add one above to get started.</div>';
          return;
        }
        let html = '';
        tasks.forEach(task => {
          const checked = task.completed ? 'checked' : '';
          const cls = task.completed ? 'completed' : '';
          html += `
            <div class="task-item">
              <input type="checkbox" ${checked} onchange="toggleTask(${task.id})">
              <span class="task-text ${cls}">${task.text}</span>
              <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </div>`;
        });
        list.innerHTML = html;
      }

      async function toggleTask(id) {
        try {
          // get current state so we can flip it
          const tasks = await (await fetch('/api/tasks')).json();
          const t = tasks.find(x => x.id === id);
          if (!t) return;
          const res = await fetch('/api/tasks/' + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: !t.completed })
          });
          if (res.ok) loadTasks();
        } catch (err) { console.error('Error toggling:', err); }
      }

      async function deleteTask(id) {
        if (!confirm('Delete this task?')) return;
        try {
          const res = await fetch('/api/tasks/' + id, { method: 'DELETE' });
          if (res.ok) loadTasks(); else alert('Error deleting task');
        } catch (err) {
          console.error('Error deleting task:', err);
          alert('Error deleting task');
        }
      }
    </script>
  </body>
</html>
'''


# Home page route (no changes made)
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# GET all tasks from DB
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks)

# POST new task to DB
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Task text is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (text, completed) VALUES (%s, %s)", (data['text'].strip(), False))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'id': new_id, 'text': data['text'].strip(), 'completed': False}), 201

# PUT update task (toggle complete)
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if 'completed' not in data:
        return jsonify({'error': 'Missing completed status'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = %s WHERE id = %s", (data['completed'], task_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'id': task_id, 'completed': data['completed']})

# DELETE task from DB
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Task deleted'})

# Run the Flask server
if __name__ == '__main__':
    print("Starting Task Manager Server...")
    print("Visit: http://localhost:5000")
    init_db()  # This creates the table if it doesn’t exist
    app.run(debug=True, host='0.0.0.0', port=5000)
