import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="todos",
    metadata={"description": "Todo tasks for semantic search"}
)

# Initialize OpenAI embeddings
try:
    embeddings_model = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    USE_EMBEDDINGS = True
except Exception as e:
    print(f"⚠️  Warning: Could not initialize OpenAI embeddings: {e}")
    USE_EMBEDDINGS = False

def add_to_vector_db(task_id, task_text, priority=None, due_date=None):
    """
    Add a task to the vector database with its embedding
    
    Args:
        task_id: Unique identifier from SQLite
        task_text: The task description
        priority: Task priority (high/medium/low)
        due_date: Task due date
    """
    if not USE_EMBEDDINGS:
        # Skip if embeddings are not available
        return False
    
    try:
        # Generate embedding
        embedding = embeddings_model.embed_query(task_text)
        
        # Prepare metadata
        metadata = {
            "priority": priority or "medium",
            "due_date": str(due_date) if due_date else "none"
        }
        
        # Add to ChromaDB
        collection.add(
            embeddings=[embedding],
            documents=[task_text],
            metadatas=[metadata],
            ids=[f"todo_{task_id}"]
        )
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not add to vector DB: {e}")
        return False

def search_similar_tasks(query, n_results=5):
    """
    Search for similar tasks using semantic search
    
    Args:
        query: Search query text
        n_results: Number of similar results to return
        
    Returns:
        List of similar tasks with their metadata
    """
    if not USE_EMBEDDINGS:
        return []
    
    try:
        # Generate query embedding
        query_embedding = embeddings_model.embed_query(query)
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        similar_tasks = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                similar_tasks.append({
                    'task': doc,
                    'id': results['ids'][0][i].replace('todo_', ''),
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })
        
        return similar_tasks
    except Exception as e:
        print(f"⚠️  Warning: Search failed: {e}")
        return []

def delete_from_vector_db(task_id):
    """
    Delete a task from the vector database
    
    Args:
        task_id: The task ID to delete
    """
    try:
        collection.delete(ids=[f"todo_{task_id}"])
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not delete from vector DB: {e}")
        return False

def get_all_tasks_from_vector_db():
    """
    Get all tasks from vector database
    
    Returns:
        List of all tasks in the vector database
    """
    try:
        results = collection.get()
        tasks = []
        if results['documents']:
            for i, doc in enumerate(results['documents']):
                tasks.append({
                    'task': doc,
                    'id': results['ids'][i].replace('todo_', ''),
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })
        return tasks
    except Exception as e:
        print(f"⚠️  Warning: Could not retrieve tasks: {e}")
        return []

def search_by_category(category_keywords, n_results=10):
    """
    Search for tasks by category using keywords
    
    Args:
        category_keywords: Keywords related to a category (e.g., "groceries shopping food")
        n_results: Number of results to return
        
    Returns:
        List of related tasks
    """
    return search_similar_tasks(category_keywords, n_results)
