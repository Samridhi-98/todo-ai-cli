import sqlite3
from datetime import datetime
from db.vector_store import add_to_vector_db, delete_from_vector_db

conn = sqlite3.connect("todos.db", check_same_thread=False)

def init_db():
    """Initialize the database with todos table"""
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS todos(
                                                     id INTEGER PRIMARY KEY,
                                                     task TEXT,
                                                     priority TEXT,
                                                     due_date DATE,
                                                     status TEXT DEFAULT 'pending',
                                                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )
                 """)
    
    # Add status column to existing tables (migration)
    try:
        conn.execute("ALTER TABLE todos ADD COLUMN status TEXT DEFAULT 'pending'")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    try:
        conn.execute("ALTER TABLE todos ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass

def add_todo(task, priority, due_date):
    """Add a new todo to the database and vector store"""
    conn.execute(
        "INSERT INTO todos(task, priority, due_date, status) VALUES(?,?,?,?)",
        (task, priority, due_date, 'pending')
    )
    conn.commit()
    todo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Also add to vector database for semantic search
    add_to_vector_db(todo_id, task, priority, due_date)
    
    return todo_id

def get_todos(status_filter=None):
    """Get todos, optionally filtered by status"""
    if status_filter:
        cursor = conn.execute("SELECT * FROM todos WHERE status = ?", (status_filter,))
    else:
        cursor = conn.execute("SELECT * FROM todos ORDER BY id DESC")
    return cursor.fetchall()

def delete_todo(todo_id):
    """Delete a todo by ID from both SQLite and vector store"""
    cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    success = cursor.rowcount > 0
    
    # Also delete from vector database
    if success:
        delete_from_vector_db(todo_id)
    
    return success

def complete_todo(todo_id):
    """Mark a todo as completed"""
    cursor = conn.execute("UPDATE todos SET status = 'completed' WHERE id = ?", (todo_id,))
    conn.commit()
    return cursor.rowcount > 0

def get_todo_by_id(todo_id):
    """Get a specific todo by ID"""
    cursor = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    return cursor.fetchone()

def get_overdue_todos():
    """Get todos that are overdue"""
    today = datetime.now().date().isoformat()
    cursor = conn.execute(
        "SELECT * FROM todos WHERE due_date < ? AND status = 'pending'",
        (today,)
    )
    return cursor.fetchall()
