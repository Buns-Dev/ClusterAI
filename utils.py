import datetime
from voice import speak

def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good Morning."
    elif hour < 18:
        greeting = "Good Afternoon."
    else:
        greeting = "Good Evening."
        
    speak(f"{greeting} What is your agenda for today?")