import json
import os

MEMORY_FILE = "nova_memory.json"

def save_memory(user_name, todo_list):
    """Saves structural session parameters directly into local JSON store."""
    data = {
        "user_name": user_name,
        "todo_list": todo_list
    }
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving memory: {e}")

def load_memory():
    """Extracts application cache state and active variables on initialization."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
    return {"user_name": None, "todo_list": []}