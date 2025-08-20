# app.py - Your Flask server
from flask import Flask, request, jsonify, render_template_string
import mysql.connector
import mysql.connector import Error

# Create the Flask app
app = Flask(__name__)

# File where we'll save tasks
TASKS_FILE = 'tasks.json'

# Function to load tasks from file
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionart=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks)

# Function to save tasks to file
def save_tasks(tasks):
    """Save tasks to the JSON file"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Route to serve the main page
@app.route('/')
def home():
    """Show the main task manager page"""
    return render_template_string(HTML_TEMPLATE)

# API Route to get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks as JSON"""
    tasks = load_tasks()
    return jsonify(tasks)

# API Route to add a new task
@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    data = request.get_json()
    
    # Validate input
    if not data or 'text' not in data:
        return jsonify({'error': 'Task text is required'}), 400
    
    # Load current tasks
    tasks = load_tasks()
    
    # Create new task with unique ID
    new_task = {
        'id': len(tasks) + 1,  # Simple ID system
        'text': data['text'].strip(),
        'completed': False
    }
    
    # Add to list and save
    tasks.append(new_task)
    save_tasks(tasks)
    
    return jsonify(new_task), 201

# API Route to update a task (mark complete/incomplete)
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task's completed status"""
    data = request.get_json()
    tasks = load_tasks()
    
    # Find the task
    for task in tasks:
        if task['id'] == task_id:
            if 'completed' in data:
                task['completed'] = data['completed']
            save_tasks(tasks)
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

# API Route to delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    tasks = load_tasks()
    
    # Filter out the task we want to delete
    original_length = len(tasks)
    tasks = [task for task in tasks if task['id'] != task_id]
    
    if len(tasks) < original_length:
        save_tasks(tasks)
        return jsonify({'message': 'Task deleted'}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404

# Your HTML template (we'll update the JavaScript to talk to our API)
HTML_TEMPLATE = '''

<!DOCTYPE html>
<html>
  <head>
    <title>My Task Manager - With Backend!</title>

    <style>
      body {
        font-family: Arial, sans-serif;
        max-width: 500px;
        margin: 50px auto;
        padding: 20px;
        background-color: #f5f5f5;
      }

      h1 {
        text-align: center;
        color: #333;
        margin-bottom: 30px;
      }

      .input-section {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
      }

      #taskInput {
        flex: 1;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 16px;
      }

      button {
        padding: 10px 15px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
      }

      button:hover {
        background-color: #0056b3;
      }

      .task-item {
        display: flex;
        align-items: center;
        padding: 10px;
        margin: 5px 0;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }

      .task-item input[type="checkbox"] {
        margin-right: 10px;
      }

      .task-text {
        flex: 1;
        margin-right: 10px;
      }

      .delete-btn {
        background-color: #dc3545;
        padding: 5px 10px;
        font-size: 12px;
      }

      .delete-btn:hover {
        background-color: #c82333;
      }

      .completed {
        text-decoration: line-through;
        opacity: 0.6;
      }

      .no-tasks {
        text-align: center;
        color: #666;
        font-style: italic;
        padding: 40px 20px;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
    </style>
  </head>
  <body>
    <h1>📝 My Task Manager (With Backend!)</h1>

    <div class="input-section">
      <input type="text" id="taskInput" placeholder="What do you need to do?" />
      <button onclick="addTask()">Add Task</button>
    </div>

    <div id="taskList">
      <!-- Tasks will go here -->
    </div>

    <script>
      // Load tasks when page loads
      document.addEventListener('DOMContentLoaded', function() {
        loadTasks();
        
        // Add Enter key support
        document.getElementById('taskInput').addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
            addTask();
          }
        });
      });
      
      // Function to load tasks from server
      async function loadTasks() {
        try {
          const response = await fetch('/api/tasks');
          const tasks = await response.json();
          displayTasks(tasks);
        } catch (error) {
          console.error('Error loading tasks:', error);
          document.getElementById('taskList').innerHTML = '<div class="no-tasks">Error loading tasks</div>';
        }
      }
      
      // Function to add a new task
      async function addTask() {
        const input = document.getElementById('taskInput');
        const taskText = input.value.trim();
        
        if (taskText === '') {
          alert('Please enter a task!');
          return;
        }
        
        try {
          // Send task to server
          const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: taskText })
          });
          
          if (response.ok) {
            input.value = '';
            loadTasks(); // Reload all tasks
          } else {
            alert('Error adding task');
          }
        } catch (error) {
          console.error('Error adding task:', error);
          alert('Error adding task');
        }
      }
      
      // Function to display tasks on the page
      function displayTasks(tasks) {
        const taskList = document.getElementById('taskList');
        
        if (tasks.length === 0) {
          taskList.innerHTML = '<div class="no-tasks">🎯 No tasks yet! Add one above to get started.</div>';
          return;
        }
        
        let html = '';
        tasks.forEach(task => {
          const checked = task.completed ? 'checked' : '';
          const completedClass = task.completed ? 'completed' : '';
          
          html += `
            <div class="task-item">
              <input type="checkbox" ${checked} onchange="toggleTask(${task.id})">
              <span class="task-text ${completedClass}">${task.text}</span>
              <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </div>
          `;
        });
        
        taskList.innerHTML = html;
      }
      
      // Function to toggle task completion
      async function toggleTask(taskId) {
        try {
          // Get current tasks to find the one we're toggling
          const response = await fetch('/api/tasks');
          const tasks = await response.json();
          const task = tasks.find(t => t.id === taskId);
          
          if (task) {
            // Toggle the status
            const updateResponse = await fetch(`/api/tasks/${taskId}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ completed: !task.completed })
            });
            
            if (updateResponse.ok) {
              loadTasks(); // Reload tasks
            }
          }
        } catch (error) {
          console.error('Error toggling task:', error);
        }
      }
      
      // Function to delete a task
      async function deleteTask(taskId) {
        if (confirm('Are you sure you want to delete this task?')) {
          try {
            const response = await fetch(`/api/tasks/${taskId}`, {
              method: 'DELETE'
            });
            
            if (response.ok) {
              loadTasks(); // Reload tasks
            } else {
              alert('Error deleting task');
            }
          } catch (error) {
            console.error('Error deleting task:', error);
            alert('Error deleting task');
          }
        }
      }
    </script>
  </body>
</html>
'''

if __name__ == '__main__':
    print("Starting Task Manager Server...")
    print("Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)