"""
Simple file-based storage for todos and conversation history
"""
import json
import os
from datetime import datetime

TODOS_FILE = "todos.json"
CONVERSATION_FILE = "conversation_history.json"

def load_todos():
    """Load todos from JSON file"""
    if not os.path.exists(TODOS_FILE):
        return []
    try:
        with open(TODOS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_todos(todos):
    """Save todos to JSON file"""
    with open(TODOS_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def add_todo(task, priority="medium", due_date=None):
    """Add a new todo"""
    todos = load_todos()
    new_id = max([t['id'] for t in todos], default=0) + 1
    
    todo = {
        'id': new_id,
        'task': task,
        'priority': priority,
        'due_date': due_date,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    todos.append(todo)
    save_todos(todos)
    return new_id

def get_todos(status_filter=None):
    """Get todos, optionally filtered by status"""
    todos = load_todos()
    if status_filter:
        todos = [t for t in todos if t['status'] == status_filter]
    return sorted(todos, key=lambda x: x['id'], reverse=True)

def delete_todo(todo_id):
    """Delete a todo by ID"""
    todos = load_todos()
    original_len = len(todos)
    todos = [t for t in todos if t['id'] != todo_id]
    
    if len(todos) < original_len:
        save_todos(todos)
        return True
    return False

def complete_todo(todo_id):
    """Mark a todo as completed"""
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['status'] = 'completed'
            save_todos(todos)
            return True
    return False

def get_overdue_todos():
    """Get overdue pending todos"""
    todos = load_todos()
    today = datetime.now().date().isoformat()
    
    overdue = []
    for todo in todos:
        if todo['status'] == 'pending' and todo.get('due_date'):
            if todo['due_date'] < today:
                overdue.append(todo)
    
    return overdue

# Conversation history functions
def load_conversation():
    """Load conversation history from file"""
    if not os.path.exists(CONVERSATION_FILE):
        return []
    try:
        with open(CONVERSATION_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_conversation(messages):
    """Save conversation history to file"""
    # Keep only last 20 messages to avoid context getting too long
    with open(CONVERSATION_FILE, 'w') as f:
        json.dump(messages[-20:], f, indent=2)

def add_message(role, content):
    """Add a message to conversation history"""
    messages = load_conversation()
    messages.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    })
    save_conversation(messages)

def clear_conversation():
    """Clear conversation history"""
    if os.path.exists(CONVERSATION_FILE):
        os.remove(CONVERSATION_FILE)
