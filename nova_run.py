import re
import os
import pyautogui
import webbrowser
import speech_recognition as sr
import queue
import threading
import keyboard
import time
import shared
import sys
import nexus_backend

UI_ENABLED = True
try:
    from ui import start_ui
except ImportError:
    UI_ENABLED = False

from voice import speak as voice_speak, take_command
from commands import process_command
from app_control import open_application, close_application, play_on_youtube, take_screenshot
from utils import wish_me

def speak(text):
    voice_speak(text)
    if UI_ENABLED:
        shared.message_queue.put({"type": "speak", "text": text})

def system_message(text):
    if UI_ENABLED:
        shared.message_queue.put({"type": "system", "text": text})

def capture_voice_and_queue():
    system_message("🎤 Listening...")
    command = take_command()
    if command and command != "none":
        shared.command_queue.put(command)
        shared.message_queue.put({"type": "listen", "text": command})

shared.voice_trigger_callback = capture_voice_and_queue

def core_intelligence_loop():
    """Loops indefinitely to process backlogged command strings."""
    wish_me()
    while True:
        try:
            time.sleep(0.1)
        except Exception:
            pass

if __name__ == "__main__":
    print("==================================================")
    print("       ✦  N O V A   I N T E L L I G E N C E  ✦    ")
    print("==================================================")
    
    shared.init() 
    nexus_backend.start_backend_engine()
    print("Nexus Core Engine Backend Activated...")
    
    if sys.platform == "win32":
        import ctypes
        try:
            myappid = "muneeb.nova.intelligencesuite.v1"
            # --- FIX THIS EXACT LINE (Make sure it says windll with two L's) ---
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Failed to set App ID: {e}")

    threading.Thread(target=core_intelligence_loop, daemon=True).start()
    
    if UI_ENABLED:
        start_ui()
    else:
        while True:
            time.sleep(1)