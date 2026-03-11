from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from db.todo_store import get_todos, get_overdue_todos
from db.vector_store import search_similar_tasks, get_all_tasks_from_vector_db
import os
from datetime import datetime, timedelta

load_dotenv()

# Initialize LLM
try:
    llm = ChatAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
        temperature=0.7
    )
    USE_LLM = True
except Exception as e:
    print(f"⚠️  Warning: Could not initialize LLM: {e}")
    USE_LLM = False

def analyze_task_patterns(todos):
    """
    Analyze historical tasks to find patterns
    
    Args:
        todos: List of todo tuples from database
        
    Returns:
        Dictionary with pattern insights
    """
    if not todos:
        return {"patterns": [], "insights": "No historical data available"}
    
    # Collect task texts
    tasks_text = [todo[1] for todo in todos if todo[1]]
    
    # Group by frequency (simple pattern detection)
    task_keywords = {}
    for task in tasks_text:
        words = task.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                task_keywords[word] = task_keywords.get(word, 0) + 1
    
    # Find common tasks
    common_keywords = sorted(task_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_tasks": len(todos),
        "common_keywords": common_keywords,
        "tasks_text": tasks_text[:10]  # Last 10 tasks for context
    }

def generate_suggestions():
    """
    Generate intelligent task suggestions based on:
    1. Historical patterns (using vector DB)
    2. Overdue tasks
    3. AI analysis
    
    Returns:
        Dictionary with suggestions and overdue tasks
    """
    # Get overdue tasks
    overdue = get_overdue_todos()
    
    # Get completed tasks for pattern analysis
    completed_todos = get_todos(status_filter='completed')
    pending_todos = get_todos(status_filter='pending')
    
    # Analyze patterns
    patterns = analyze_task_patterns(completed_todos + pending_todos)
    
    suggestions = {
        "overdue": [],
        "pattern_based": [],
        "ai_suggestions": []
    }
    
    # Format overdue tasks
    if overdue:
        for todo in overdue:
            suggestions["overdue"].append({
                "id": todo[0],
                "task": todo[1],
                "due_date": todo[3],
                "priority": todo[2]
            })
    
    # Generate pattern-based suggestions using LLM
    if USE_LLM and patterns["tasks_text"]:
        try:
            prompt = f"""
Based on the user's todo history, suggest 3 new tasks they might want to add.

Historical tasks:
{', '.join(patterns["tasks_text"])}

Common themes: {', '.join([kw[0] for kw in patterns["common_keywords"][:3]])}

Provide 3 short, actionable task suggestions that fit their patterns.
Format as a simple list, one per line, no numbering or bullets.
"""
            
            response = llm.invoke(prompt)
            ai_suggestions = response.content.strip().split('\n')
            suggestions["ai_suggestions"] = [s.strip() for s in ai_suggestions if s.strip()][:3]
            
        except Exception as e:
            print(f"⚠️  Could not generate AI suggestions: {e}")
    
    # Pattern-based suggestions (rule-based fallback)
    if patterns["common_keywords"]:
        for keyword, count in patterns["common_keywords"][:3]:
            if count > 1:
                suggestions["pattern_based"].append({
                    "keyword": keyword,
                    "frequency": count,
                    "suggestion": f"Review tasks related to '{keyword}' (appears {count} times)"
                })
    
    return suggestions

def get_similar_to_task(task_text, n_results=3):
    """
    Find similar tasks to a given task using vector search
    
    Args:
        task_text: The task to find similar tasks for
        n_results: Number of similar tasks to return
        
    Returns:
        List of similar tasks
    """
    similar = search_similar_tasks(task_text, n_results)
    return similar

def suggest_next_tasks():
    """
    Main function to generate and format suggestions
    
    Returns:
        Formatted string with all suggestions
    """
    suggestions = generate_suggestions()
    
    output = "\n" + "="*80 + "\n"
    output += "🤖 AI-POWERED TASK SUGGESTIONS\n"
    output += "="*80 + "\n\n"
    
    # Show overdue tasks first
    if suggestions["overdue"]:
        output += "⚠️  OVERDUE TASKS (Action Required!):\n"
        output += "-" * 80 + "\n"
        for task in suggestions["overdue"]:
            priority_emoji = "🔴" if task["priority"] == "high" else "🟡"
            output += f"  {priority_emoji} #{task['id']} - {task['task']}\n"
            output += f"     Due: {task['due_date']} ({task['priority']} priority)\n\n"
    
    # Show AI suggestions
    if suggestions["ai_suggestions"]:
        output += "💡 SMART SUGGESTIONS (Based on Your Patterns):\n"
        output += "-" * 80 + "\n"
        for i, suggestion in enumerate(suggestions["ai_suggestions"], 1):
            output += f"  {i}. {suggestion}\n"
        output += "\n"
    
    # Show pattern insights
    if suggestions["pattern_based"]:
        output += "📊 PATTERN INSIGHTS:\n"
        output += "-" * 80 + "\n"
        for pattern in suggestions["pattern_based"]:
            output += f"  • {pattern['suggestion']}\n"
        output += "\n"
    
    if not suggestions["overdue"] and not suggestions["ai_suggestions"] and not suggestions["pattern_based"]:
        output += "✅ All caught up! No urgent suggestions at the moment.\n"
        output += "💡 Add more tasks to help me learn your patterns.\n\n"
    
    output += "="*80 + "\n"
    
    return output
