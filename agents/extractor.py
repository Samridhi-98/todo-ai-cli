from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
import json

load_dotenv()

try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in .env file")
        USE_REAL_LLM = False
    else:
        llm = ChatAnthropic(api_key=api_key, model="claude-3-5-sonnet-20241022")
        USE_REAL_LLM = True
        print("✅ Claude AI initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize Claude: {e}")
    USE_REAL_LLM = False

def extract_task(text):
    if USE_REAL_LLM:
        try:
            prompt = f"""
            Extract a todo task, priority and date.

            Input: {text}

            Return JSON with fields:
            task, priority, due_date
            """

            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"LLM API error: {e}")
            return simple_extract(text)
    else:
        return simple_extract(text)

def simple_extract(text):
    result = {
        "task": text.strip(),
        "priority": "medium",
        "due_date": None
    }
    
    # Extract priority
    if any(word in text.lower() for word in ['urgent', 'asap', 'high']):
        result["priority"] = "high"
    elif any(word in text.lower() for word in ['low', 'later']):
        result["priority"] = "low"
    
    # Extract date (simple pattern matching)
    import re
    date_patterns = [
        r'\b(tomorrow|today|next week|next month)\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(in \d+ days?|in \d+ weeks?)\b'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["due_date"] = match.group()
            break
    
    return json.dumps(result)
