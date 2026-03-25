"""
Simple AI-powered Todo CLI
A conversational chatbot for managing your tasks
"""
from storage import (
    add_todo, get_todos, delete_todo, 
    complete_todo, get_overdue_todos, clear_conversation
)
from chatbot import extract_task_details, chat_with_history, suggest_next_tasks
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def print_todos(todos):
    """Display todos in a nice formatted table"""
    if not todos:
        console.print("📭 [yellow]No todos found![/yellow]")
        return
    
    table = Table(title="📋 Your Todos", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Task", style="cyan", width=40)
    table.add_column("Priority", width=12)
    table.add_column("Due Date", width=15)
    table.add_column("Status", width=12)
    
    for todo in todos:
        todo_id = str(todo['id'])
        task = todo['task']
        priority = todo.get('priority', 'medium')
        due_date = todo.get('due_date') or "No date"
        status = todo.get('status', 'pending')
        
        # Status emoji and styling
        if status == "completed":
            status_display = "✅ completed"
            style = "dim"
        else:
            status_display = "⏳ pending"
            style = ""
        
        # Priority emoji
        if priority == "high":
            priority_display = "🔴 high"
        elif priority == "low":
            priority_display = "🟢 low"
        else:
            priority_display = "🟡 medium"
        
        table.add_row(todo_id, task, priority_display, due_date, status_display, style=style)
    
    console.print(table)

def print_help():
    """Display help information"""
    help_text = """
# 🤖 Todo AI CLI - Commands

## Direct Commands:
- **add <task>** - Add a new task (e.g., "add buy groceries tomorrow")
- **list** - Show all todos
- **list pending** - Show only pending todos
- **list completed** - Show only completed todos
- **complete <id>** - Mark a todo as completed
- **delete <id>** - Delete a todo
- **suggest** - Get AI-powered task suggestions
- **overdue** - Show overdue tasks
- **clear** - Clear conversation history
- **help** - Show this help message
- **exit** - Exit the application

## Natural Language:
You can also chat naturally! The bot remembers your conversation. Try:
- "What tasks do I have?"
- "Show me my high priority tasks"
- "What should I work on next?"
- "Remind me what we talked about"

## Examples:
```
> add finish report by friday high priority
> list pending
> complete 1
> suggest
> what did I just add?
```
"""
    console.print(Panel(Markdown(help_text), title="Help", border_style="blue"))

def print_welcome():
    """Display welcome message"""
    welcome = Panel(
        "[bold cyan]🤖 Welcome to Todo AI CLI![/bold cyan]\n\n"
        "Your intelligent task manager powered by OpenAI.\n"
        "Type [bold green]'help'[/bold green] to see available commands or just chat naturally!\n"
        "[dim]I remember our conversations, so feel free to reference previous topics.[/dim]",
        title="Welcome",
        border_style="green"
    )
    console.print(welcome)

def handle_command(cmd):
    """Handle user commands"""
    cmd = cmd.strip()
    
    if not cmd:
        return True
    
    # Add command
    if cmd.startswith("add "):
        text = cmd.replace("add ", "", 1).strip()
        if not text:
            console.print("❌ [red]Please provide a task description.[/red]")
            return True
        
        # Extract task details using AI
        console.print("🤔 [cyan]Analyzing your task...[/cyan]")
        task_data = extract_task_details(text)
        
        task_name = task_data.get("task", text)
        priority = task_data.get("priority", "medium")
        due_date = task_data.get("due_date")
        
        add_todo(task_name, priority, due_date)
        
        console.print("\n✅ [green]Task added successfully![/green]")
        console.print(f"   📝 Task: [bold]{task_name}[/bold]")
        console.print(f"   🎯 Priority: [bold]{priority}[/bold]")
        if due_date:
            console.print(f"   📅 Due: [bold]{due_date}[/bold]")
        console.print()
    
    # List commands
    elif cmd.startswith("list"):
        parts = cmd.split()
        if len(parts) > 1:
            status_filter = parts[1]
            todos = get_todos(status_filter=status_filter)
            console.print(f"\n[bold]📋 {status_filter.capitalize()} Todos:[/bold]")
        else:
            todos = get_todos()
            console.print("\n[bold]📋 All Todos:[/bold]")
        
        print_todos(todos)
        console.print()
    
    # Delete command
    elif cmd.startswith("delete "):
        parts = cmd.split()
        if len(parts) < 2:
            console.print("❌ [red]Please provide a todo ID. Usage: delete <id>[/red]")
            return True
        
        try:
            todo_id = int(parts[1])
            if delete_todo(todo_id):
                console.print(f"✅ [green]Todo #{todo_id} deleted successfully![/green]\n")
            else:
                console.print(f"❌ [red]Todo #{todo_id} not found.[/red]\n")
        except ValueError:
            console.print("❌ [red]Invalid ID. Please provide a number.[/red]\n")
    
    # Complete command
    elif cmd.startswith("complete "):
        parts = cmd.split()
        if len(parts) < 2:
            console.print("❌ [red]Please provide a todo ID. Usage: complete <id>[/red]")
            return True
        
        try:
            todo_id = int(parts[1])
            if complete_todo(todo_id):
                console.print(f"✅ [green]Todo #{todo_id} marked as completed! 🎉[/green]\n")
            else:
                console.print(f"❌ [red]Todo #{todo_id} not found.[/red]\n")
        except ValueError:
            console.print("❌ [red]Invalid ID. Please provide a number.[/red]\n")
    
    # Suggest command
    elif cmd == "suggest":
        console.print("\n🔮 [cyan]Analyzing your tasks and generating suggestions...[/cyan]\n")
        todos = get_todos()
        suggestions = suggest_next_tasks(todos)
        
        console.print(Panel(suggestions, title="💡 AI Suggestions", border_style="yellow"))
        console.print()
    
    # Overdue command
    elif cmd == "overdue":
        overdue = get_overdue_todos()
        if overdue:
            console.print("\n⚠️  [bold red]Overdue Tasks:[/bold red]")
            print_todos(overdue)
        else:
            console.print("\n✅ [green]No overdue tasks! You're all caught up![/green]\n")
    
    # Clear conversation history
    elif cmd == "clear":
        clear_conversation()
        console.print("🗑️  [yellow]Conversation history cleared![/yellow]\n")
    
    # Help command
    elif cmd == "help":
        print_help()
    
    # Exit command
    elif cmd in ["exit", "quit", "q"]:
        console.print("\n👋 [cyan]Goodbye! Stay productive![/cyan]\n")
        return False
    
    # Natural language - use chatbot with conversation history
    else:
        console.print("🤔 [cyan]Let me think...[/cyan]")
        
        # Get todos context for the chatbot
        todos = get_todos()
        if todos:
            todos_context = "\n".join([
                f"#{todo['id']}: {todo['task']} ({todo['status']})"
                for todo in todos[:5]
            ])
        else:
            todos_context = "No todos yet."
        
        response = chat_with_history(cmd, todos_context)
        console.print(f"\n🤖 [bold cyan]{response}[/bold cyan]\n")
    
    return True

def main():
    """Main application loop"""
    print_welcome()
    console.print()
    
    while True:
        try:
            user_input = console.input("[bold green]> [/bold green]").strip()
            
            if not user_input:
                continue
            
            should_continue = handle_command(user_input)
            if should_continue is False:
                break
        
        except KeyboardInterrupt:
            console.print("\n\n👋 [cyan]Goodbye! Stay productive![/cyan]\n")
            break
        except Exception as e:
            console.print(f"\n❌ [red]Error: {e}[/red]\n")

if __name__ == "__main__":
    main()
