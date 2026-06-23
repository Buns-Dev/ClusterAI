import re
import datetime
import webbrowser
from weather import get_weather_simple
from news import get_news
# 👇 WE ADDED THE MISSING APP CONTROL IMPORTS HERE
from app_control import get_battery, open_application, close_application 
from memory import load_memory, save_memory

user_name = None
todo_list = []
last_weather_city = None

def init_memory():
    global user_name, todo_list
    data = load_memory()
    user_name = data.get("user_name")
    todo_list = data.get("todo_list", [])

init_memory()

def save_state():
    save_memory(user_name, todo_list)

def process_command(user_input):
    """
    TOOL EXECUTION MODULE
    Only processes explicit system tools. General conversation and math 
    are handled dynamically by the Nexus Local LLM Core.
    """
    global user_name, todo_list, last_weather_city
    text = user_input.lower()

    # --- HARDWARE & APP CONTROL TOOLS (NEWLY LINKED!) ---
    if text.startswith("open ") or text.startswith("launch "):
        app_name = text.replace("open ", "").replace("launch ", "").strip()
        open_application(app_name)
        return {
            "ui": f"⚙️ SYSTEM PROTOCOL :: Launching '{app_name}'...",
            "voice": f"Opening {app_name} now."
        }
        
    if text.startswith("close ") or text.startswith("terminate "):
        app_name = text.replace("close ", "").replace("terminate ", "").strip()
        close_application(app_name)
        return {
            "ui": f"⚙️ SYSTEM PROTOCOL :: Terminating '{app_name}'...",
            "voice": f"Closing {app_name}."
        }

    # --- MEMORY & IDENTITY TOOLS ---
    if "my name is" in text:
        user_name = text.split("my name is")[-1].strip()
        save_state()
        return f"Identity registered. Nice to meet you, {user_name}."
    
    if "what's my name" in text or "do you know my name" in text or "say my name" in text:
        if user_name:
            return f"Your designated user identity is {user_name}."
        return "I don't have a name registered for you yet."

    # --- SYSTEM TELEMETRY TOOLS ---
    if (last_weather_city and 
        ("celsius" in text or "centigrade" in text or "degree" in text or "cel" in text) and
        not any(x in text for x in ["weather", "news", "time", "volume", "open", "close"])):
        return get_weather_simple(last_weather_city)

    if "weather" in text or "temperature" in text:
        city_match = re.search(r'in\s+([a-zA-Z\s]+)', text)
        city = city_match.group(1).strip() if city_match else ""
        weather_info = get_weather_simple(city) if city else get_weather_simple("London")
        
        if isinstance(weather_info, dict) and "FAILURE" not in weather_info.get("ui", ""):
             last_weather_city = city if city else "London"
        return weather_info

    if "news" in text or "headlines" in text:
        source = "bbc"
        if "tech" in text or "technology" in text:
            source = "techcrunch"
        elif "reuters" in text:
            source = "reuters"
        elif "cnn" in text:
            source = "cnn"
        return get_news(source)

    if "battery" in text or "power" in text:
        return get_battery()

    if "time" in text and not ("volume" in text or "up" in text):
        return "The current system time is " + datetime.datetime.now().strftime("%I:%M %p")
    
    if "date" in text or "today" in text:
        return "Today's date is " + datetime.datetime.now().strftime("%A, %B %d, %Y")

    # --- EXTERNAL SEARCH TOOL (FIXED) ---
    # We changed the trigger so "what is" goes safely to Llama 3.2. 
    # To use Google, you must explicitly say "search the web for" or "google".
    if "search the web for" in text or "google" in text:
        target = text.replace("search the web for", "").replace("google", "").strip()
        if target:
            webbrowser.open(f"https://www.google.com/search?q={target.replace(' ', '+')}")
            return {
                "ui": f"🌐 UPLINK ACTIVATED :: Executing web search for '{target}'",
                "voice": f"Pulling up search results for {target}."
            }

    # --- TASK MANAGEMENT TOOL ---
    if "add task" in text or "add to do" in text:
        task = re.sub(r"(add task|add to do)", "", text).strip()
        if task and len(task) > 2:
            todo_list.append(task)
            save_state()
            return f"Task '{task}' added to the tracking grid."
        return "Please specify the task parameters."
    
    if any(x in text for x in ["show tasks", "show task", "what's on my", "show to do", "todo", "to do"]):
        if todo_list:
            return "Active Task Grid: " + ", ".join(todo_list)
        return "Task grid is currently empty."
    
    if any(x in text for x in ["clear tasks", "clear task", "delete tasks", "delete task"]):
        todo_list.clear()
        save_state()
        return "Task grid wiped successfully."

    # --- DYNAMIC ROUTING FALLBACK ---
    # If no specific tool was triggered, it safely passes to the Llama 3.2 Core.
    return None