import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from storage import load_conversation, add_message

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def extract_task_details(user_input):
    if not client:
        return simple_extract(user_input)
    
    try:
        system_prompt = """You are a helpful assistant that extracts todo task information from natural language.
Extract the task name, priority (high/medium/low), and due date from the user's input.

Return ONLY a JSON object with these fields:
- task: the main task description (string)
- priority: one of "high", "medium", or "low" (string)
- due_date: the due date if mentioned, or null (string or null)

Examples:
Input: "buy groceries tomorrow"
Output: {"task": "buy groceries", "priority": "medium", "due_date": "tomorrow"}

Input: "urgent: finish report by friday"
Output: {"task": "finish report", "priority": "high", "due_date": "friday"}

Input: "call mom"
Output: {"task": "call mom", "priority": "medium", "due_date": null}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON from response
        try:
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            task_data = json.loads(content)
            return task_data
        except json.JSONDecodeError:
            print(f"⚠️  Could not parse JSON from OpenAI response: {content}")
            return simple_extract(user_input)
            
    except Exception as e:
        print(f"⚠️  OpenAI API error: {e}")
        return simple_extract(user_input)


def simple_extract(text):
    import re
    
    result = {
        "task": text.strip(),
        "priority": "medium",
        "due_date": None
    }

    text_lower = text.lower()
    if any(word in text_lower for word in ['urgent', 'asap', 'high', 'important']):
        result["priority"] = "high"
    elif any(word in text_lower for word in ['low', 'later', 'sometime']):
        result["priority"] = "low"

    date_patterns = [
        r'\b(tomorrow|today|tonight)\b',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(next week|next month|this week)\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\bin (\d+) (day|days|week|weeks)\b'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["due_date"] = match.group()
            break

    task_text = text
    for word in ['urgent', 'asap', 'high priority', 'low priority', 'important']:
        task_text = re.sub(rf'\b{word}\b', '', task_text, flags=re.IGNORECASE)
    
    result["task"] = task_text.strip()
    
    return result


def chat_with_history(user_message, todos_context=None):
    if not client:
        return "I'm running in offline mode. Use 'add', 'list', 'complete', or 'delete' commands."
    
    try:
        history = load_conversation()

        context = ""
        if todos_context:
            context = f"\n\nCurrent todos:\n{todos_context}"
        
        system_prompt = f"""You are a helpful todo assistant. You help users manage their tasks.
You can help them add tasks, view their task list, mark tasks as complete, and delete tasks.

Be friendly, concise, and helpful. If the user asks about their tasks, use the context provided.
Remember previous conversations to provide better assistance.
{context}
"""

        messages = [{"role": "system", "content": system_prompt}]

        for msg in history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        assistant_response = response.choices[0].message.content.strip()
        
        add_message("user", user_message)
        add_message("assistant", assistant_response)
        
        return assistant_response
        
    except Exception as e:
        print(f"⚠️  Chat error: {e}")
        return "I'm having trouble responding right now. Please try using specific commands like 'add', 'list', 'complete', or 'delete'."


def suggest_next_tasks(todos):
    if not client or not todos:
        return "No suggestions available at the moment."
    
    try:
        todos_text = "\n".join([
            f"- {todo['task']} (Priority: {todo['priority']}, Due: {todo.get('due_date') or 'No date'}, Status: {todo['status']})"
            for todo in todos[:10]
        ])
        
        system_prompt = """You are a productivity assistant. Based on the user's current tasks, 
suggest 3 actionable next steps or new tasks they might want to add.
Be specific and practical. Format your response as a numbered list."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here are my current tasks:\n{todos_text}\n\nWhat should I focus on next?"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"⚠️  Suggestion error: {e}")
        return "Could not generate suggestions at this time."
