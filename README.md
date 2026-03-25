# Todo AI CLI

A simple AI-powered command-line todo list application with conversational interface, built with Python and OpenAI.

## Features

- 🤖 **AI-Powered Task Extraction** - Add todos using natural language
- 💬 **Conversational Interface** - Chat naturally with your todo assistant
- 🧠 **Conversation Memory** - The bot remembers your previous conversations
- 📝 **Smart Task Management** - Automatic priority and due date detection
- 🎯 **Task Suggestions** - Get AI-powered recommendations on what to work on next
- 💾 **File-Based Storage** - Simple JSON files keep your tasks and conversation history
- 🎨 **Beautiful CLI** - Rich formatting with colors and emojis

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

### 1. Clone the repository
```bash
cd /Users/samridhiagrawal/Projects/ai/todo-ai-cli
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

## Usage

### Start the application
```bash
python main.py
```

### Available Commands

#### Direct Commands:
- `add <task>` - Add a new task
  - Example: `add buy groceries tomorrow`
  - Example: `add finish report by friday high priority`
- `list` - Display all todos
- `list pending` - Show only pending todos
- `list completed` - Show only completed todos
- `complete <id>` - Mark a todo as completed
- `delete <id>` - Delete a todo
- `suggest` - Get AI-powered task suggestions
- `overdue` - Show overdue tasks
- `clear` - Clear conversation history
- `help` - Show help message
- `exit` - Exit the application

#### Natural Language with Memory:
The bot remembers your previous conversations! You can:
- Ask follow-up questions
- Reference previous topics
- Have a natural conversation flow

Examples:
- "What tasks do I have?"
- "Show me my high priority tasks"
- "What should I work on next?"
- "What did I just add?"
- "Remind me what we talked about earlier"

## Examples

```bash
# Add a task with natural language
> add buy groceries tomorrow high priority
🤔 Analyzing your task...
✅ Task added successfully!
   📝 Task: buy groceries
   🎯 Priority: high
   📅 Due: tomorrow

# List all tasks
> list
📋 All Todos:
┌────┬─────────────────┬──────────┬─────────┬───────────┐
│ ID │ Task            │ Priority │ Due Date│ Status    │
├────┼─────────────────┼──────────┼─────────┼───────────┤
│ 1  │ buy groceries   │ 🔴 high  │ tomorrow│ ⏳ pending│
└────┴─────────────────┴──────────┴─────────┴───────────┘

# Natural conversation with memory
> what did I just add?
🤖 You just added a task to buy groceries tomorrow with high priority!

> should I do that today or tomorrow?
🤖 Since you set the due date for tomorrow, you have until then. However,
    since it's high priority, you might want to consider doing it today...

# Mark as complete
> complete 1
✅ Todo #1 marked as completed! 🎉

# Get AI suggestions
> suggest
🔮 Analyzing your tasks and generating suggestions...
💡 AI Suggestions
Based on your tasks, here are some suggestions...
```

## Project Structure

```
.
├── main.py                      # Main entry point with CLI interface
├── chatbot.py                   # OpenAI chatbot with conversation memory
├── storage.py                   # File-based storage for todos and conversations
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── todos.json                   # Todos storage (created automatically)
├── conversation_history.json    # Conversation memory (created automatically)
└── README.md                    # This file
```

## Key Features Explained

### 1. Natural Language Processing
The app uses OpenAI's GPT-3.5 to understand your tasks in plain English:
- Extracts task name, priority, and due dates automatically
- Understands contexts like "urgent", "tomorrow", "next week"

### 2. Conversational Interface with Memory
The bot maintains conversation history in a file:
- Remembers what you talked about
- Can reference previous topics
- Provides contextual responses
- Creates a more natural chat experience

### 3. Smart Suggestions
The AI analyzes your task patterns and suggests:
- What to work on next
- Task prioritization
- Productivity tips

### 4. Simple File Storage
All data is stored in JSON files:
- `todos.json` - Your task list
- `conversation_history.json` - Chat history (last 20 messages)
- No complex database setup needed
- Easy to backup and version control

## Data Storage

### Todos (todos.json)
```json
[
  {
    "id": 1,
    "task": "buy groceries",
    "priority": "high",
    "due_date": "tomorrow",
    "status": "pending",
    "created_at": "2026-03-25T16:54:00"
  }
]
```

### Conversation History (conversation_history.json)
```json
[
  {
    "role": "user",
    "content": "what tasks do I have?",
    "timestamp": "2026-03-25T16:55:00"
  },
  {
    "role": "assistant",
    "content": "You have 1 pending task...",
    "timestamp": "2026-03-25T16:55:01"
  }
]
```

## Conversation Management

- Conversation history is stored in `conversation_history.json`
- Last 20 messages are kept to avoid context getting too long
- Use `clear` command to reset conversation history
- History is automatically loaded on each interaction

## Offline Mode

If the OpenAI API is unavailable or not configured, the app falls back to:
- Rule-based task extraction
- Basic command functionality
- No AI chat or suggestions

## License

This is a learning project demonstrating:
- OpenAI API integration
- Python CLI development
- File-based data storage
- Conversational AI with memory

## Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Make sure you've created a `.env` file
- Check that your API key is correctly set in `.env`

**Error: "Module not found"**
- Activate your virtual environment
- Run `pip install -r requirements.txt`

**Tasks not saving**
- Check that you have write permissions in the directory
- The `todos.json` file should be created automatically

**Conversation history not working**
- The `conversation_history.json` file is created automatically
- Use the `clear` command if you want to reset it

## Contributing

Feel free to fork this project and make improvements! This is a learning project, so contributions are welcome.
