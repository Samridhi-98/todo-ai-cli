import json
from graph import workflow
from db.todo_store import (
    add_todo, get_todos, init_db, 
    delete_todo, complete_todo, get_overdue_todos
)
from agents.suggester import suggest_next_tasks


init_db()

def print_todos(todos):
    if not todos:
        print("📭 No todos found!")
        return
    
    print("\n" + "="*80)
    print(f"{'ID':<5} {'Task':<35} {'Priority':<10} {'Due Date':<12} {'Status':<10}")
    print("="*80)
    
    for todo in todos:
        todo_id = todo[0]
        task = todo[1][:32] + "..." if len(todo[1]) > 32 else todo[1]
        priority = todo[2] or "medium"
        due_date = todo[3] or "No date"
        status = todo[4] if len(todo) > 4 else "pending"

        status_emoji = "✅" if status == "completed" else "⏳"

        if priority == "high":
            priority_display = f"🔴 {priority}"
        elif priority == "low":
            priority_display = f"🟢 {priority}"
        else:
            priority_display = f"🟡 {priority}"
        
        print(f"{todo_id:<5} {task:<35} {priority_display:<15} {due_date:<12} {status_emoji} {status}")
    
    print("="*80 + "\n")

print("🤖 Welcome to Todo AI CLI!")

while True:
    try:
        cmd = input("> ").strip()
        
        if not cmd:
            continue
        
        if cmd.startswith("add"):
            text = cmd.replace("add", "", 1).strip()
            if not text:
                print("❌ Please provide a task description.")
                continue
            
            result = workflow.invoke({"text": text})
            extracted_str = str(result.get("task", ""))
            
            try:
                start_idx = extracted_str.find('{')
                end_idx = extracted_str.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = extracted_str[start_idx:end_idx+1]
                    data = json.loads(json_str)
                    
                    task_name = data.get("task", text)
                    priority = data.get("priority", "medium")
                    due_date = data.get("due_date", None)
                    
                    add_todo(task_name, priority, due_date)
                    print("✅ Task added successfully to database!")
                    print("AI Properties Extracted:", data)
                else:
                    add_todo(text, "medium", None)
                    print("✅ Task added successfully to database (without AI extraction)!")
            except Exception as e:
                add_todo(text, "medium", None)
                print(f"✅ Task added successfully to database (fallback due to error: {e})!")
        
        elif cmd.startswith("list"):
            parts = cmd.split()
            if len(parts) > 1:
                status_filter = parts[1]
                todos = get_todos(status_filter=status_filter)
                print(f"\n📋 {status_filter.capitalize()} Todos:")
            else:
                todos = get_todos()
                print("\n📋 All Todos:")
            
            print_todos(todos)
        
        elif cmd.startswith("delete"):
            parts = cmd.split()
            if len(parts) < 2:
                print("❌ Please provide a todo ID. Usage: delete <id>")
                continue
            
            try:
                todo_id = int(parts[1])
                if delete_todo(todo_id):
                    print(f"✅ Todo #{todo_id} deleted successfully!")
                else:
                    print(f"❌ Todo #{todo_id} not found.")
            except ValueError:
                print("❌ Invalid ID. Please provide a number.")
        
        elif cmd.startswith("complete"):
            parts = cmd.split()
            if len(parts) < 2:
                print("❌ Please provide a todo ID. Usage: complete <id>")
                continue
            
            try:
                todo_id = int(parts[1])
                if complete_todo(todo_id):
                    print(f"✅ Todo #{todo_id} marked as completed! 🎉")
                else:
                    print(f"❌ Todo #{todo_id} not found.")
            except ValueError:
                print("❌ Invalid ID. Please provide a number.")
        
        elif cmd == "suggest":
            print("\n🔮 Analyzing your tasks and generating suggestions...\n")
            suggestions = suggest_next_tasks()
            print(suggestions)
        
        elif cmd == "exit":
            print("👋 Goodbye! Happy productivity!")
            break
        
        else:
            print(f"❌ Unknown command: '{cmd}'. Type 'help' to see available commands.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Happy productivity!")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
