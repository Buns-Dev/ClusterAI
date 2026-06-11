import re
import datetime
import random
import webbrowser
from weather import get_weather_simple
from news import get_news
from app_control import get_battery
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
    global user_name, todo_list, last_weather_city
    text = user_input.lower()

    if "my name is" in text:
        user_name = text.split("my name is")[-1].strip()
        save_state()
        return f"Nice to meet you, {user_name}!"
    
    if "what's my name" in text or "do you know my name" in text or "say my name" in text:
        if user_name:
            return f"Your name is {user_name}."
        return "I don't know your name yet. You can tell me by saying 'my name is ...'"

    if any(x in text for x in ["who are you", "what are you", "your name", "who r u", "hu r u"]):
        return (
            "I am Nova. In the vastness of the cosmos, a nova is a star that suddenly "
            "ignites with immense energy, increasing its brilliance by thousands of times "
            "to illuminate the darkest corners of space before returning to its quiet state.\n\n"
            "Like my namesake, I am engineered to bring a sudden flash of clarity, deep intelligence, "
            "and bright inspiration to your thoughts and tasks—standing ready to ignite into action "
            "whenever you call upon me, and resting quietly in the background when your day is won. "
            "What shall we illuminate together today?"
        )

    if any(g in text for g in ["hello", "hi", "hey"]):
        return "Hello! How can I assist you?"
    
    if "how are you" in text:
        return "I am functioning optimally. How can I help you?"
        
    if "thank you" in text or "thanks" in text:
        return "You're welcome!"
        
    if "what can you do" in text:
        return "I can tell time, do math, search Wikipedia, open apps, play music, control volume, take screenshots, remember your name, tell jokes, manage a to-do list, give weather, news, battery status, and more."

    if (last_weather_city and 
        ("celsius" in text or "centigrade" in text or "degree" in text or "cel" in text) and
        not any(x in text for x in ["weather", "news", "time", "volume", "open", "close"])):
        return get_weather_simple(last_weather_city)

    if "weather" in text or "temperature" in text:
        city_match = re.search(r'in\s+([a-zA-Z\s]+)', text)
        city = city_match.group(1).strip() if city_match else ""
        weather_info = get_weather_simple(city) if city else get_weather_simple()
        if "unavailable" not in weather_info and "Could not" not in weather_info:
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

    if "battery" in text:
        return get_battery()

    if "time" in text and not ("volume" in text or "up" in text):
        return "The time is " + datetime.datetime.now().strftime("%I:%M %p")
    if "date" in text or "today" in text:
        return "Today is " + datetime.datetime.now().strftime("%A, %B %d, %Y")

    if re.search(r'\d', text) and (re.search(r'[\+\-\*\/x]', text) or any(op in text for op in ["plus","minus","times","divided"])):
        try:
            expr = text.replace("plus","+").replace("minus","-").replace("times","*").replace("multiplied by","*").replace("multiply by","*")
            expr = expr.replace("divided by","/").replace("divide","/").replace("divide by","/").replace(" x ","*").replace("x","*")
            expr = "".join(c for c in expr if c in "0123456789.+-*/()")
            result = eval(expr)
            if isinstance(result, float) and result % 1 != 0:
                return f"The answer is {result:.2f}"
            return f"The answer is {result}"
        except:
            pass

    if any(x in text for x in ["who is", "what is", "tell me about"]):
        target = re.sub(r"(who is|what is|tell me about)", "", text).replace("?", "").strip()
        if target and len(target) > 2:
            try:
                import wikipedia
                results = wikipedia.search(target, results=3)
                if results:
                    summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False)
                    return f"According to Wikipedia: {summary}"
            except:
                webbrowser.open(f"https://www.google.com/search?q={target.replace(' ', '+')}")
                return f"I searched Google for {target}."

    if "tell me a joke" in text or "make me laugh" in text:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the AI cross the road? To optimize the other side.",
            "I told my computer I needed a break, and now it won't stop sending me vacation ads."
        ]
        return random.choice(jokes)

    if "what do you think about" in text:
        topic = text.split("about")[-1].strip()
        opinions = {
            "life": "Life is fascinating. I'm here to help you live it better.",
            "ai": "I'm a simple AI, but I love helping people.",
            "python": "Python is a wonderful language for AI.",
            "space": "Space is vast and full of mysteries.",
            "music": "Music is the universal language of emotion."
        }
        return opinions.get(topic, f"I don't have a strong opinion on {topic} yet.")

    if "add task" in text or "add to do" in text:
        task = re.sub(r"(add task|add to do)", "", text).strip()
        if task and len(task) > 2:
            todo_list.append(task)
            save_state()
            return f"Added '{task}' to your to-do list."
        return "What task should I add? (say something meaningful)"
    
    if any(x in text for x in ["show tasks", "show task", "what's on my", "show to do", "todo", "to do"]):
        if todo_list:
            return "Your to-do list: " + ", ".join(todo_list)
        return "Your to-do list is empty."
    
    if any(x in text for x in ["clear tasks", "clear task", "delete tasks", "delete task"]):
        todo_list.clear()
        save_state()
        return "Cleared your to-do list."

    return "I'm not sure how to help with that. Try asking about time, calculations, Wikipedia, weather, news, or use 'help'."