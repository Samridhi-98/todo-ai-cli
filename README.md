# Todo AI CLI

An AI-powered command-line todo list application built with Python and LangGraph for learning agentic AI.

## Features

- Add todos using natural language
- AI extracts task details, priority, and due dates
- SQLite database for persistent storage
- Interactive CLI interface

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

### 1. Clone the repository (if not already done)
```bash
cd /Users/samridhiagrawal/Projects/ai/todo-ai-cli
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
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

Alternatively, you can export the environment variable directly:
```bash
export OPENAI_API_KEY='sk-your-actual-api-key-here'
```

## Usage

### Option 1: Using the run script (Easiest)
```bash
# Set your OpenAI API key first
export OPENAI_API_KEY='sk-your-actual-api-key-here'

# Run the application
./run.sh
```

### Option 2: Direct execution
```bash
# Make sure to use the Python from your venv
./venv/bin/python3 main.py
```

### Available Commands

- `add <task description>` - Add a new todo with natural language (e.g., "add buy groceries tomorrow high priority")
- `list` - Display all todos
- `exit` - Exit the application

## Project Structure

```
.
├── main.py              # Main entry point
├── graph.py             # LangGraph workflow definition
├── agents/
│   ├── extractor.py     # AI agent for extracting todo details
│   └── planner.py       # Planner agent (work in progress)
├── models/
│   └── todo.py          # Todo data model
├── db/
│   └── todo_store.py    # SQLite database operations
└── requirements.txt     # Python dependencies
```

## Learning Resources

This project demonstrates:
- **LangGraph**: Building stateful AI workflows
- **LangChain**: Working with LLMs and chat models
- **Agentic AI**: Creating AI agents that perform specific tasks
- **Python CLI**: Building interactive command-line applications
- **SQLite**: Database operations in Python

## License

This is a learning project.
