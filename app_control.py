# app_control.py – open/close apps, screenshot, YouTube, battery
import os
import webbrowser
import pywhatkit
import pyautogui
import psutil
from AppOpener import open as open_app, close as close_app

def open_application(app_name):
    """Open an application by name."""
    if app_name in ["edge", "microsoft edge"]:
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for path in edge_paths:
            if os.path.exists(path):
                os.startfile(path)
                return
        open_app("edge", match_closest=True)
    else:
        open_app(app_name, match_closest=True)

def close_application(app_name):
    """Close an application by name, using taskkill for common ones."""
    process_map = {
        "edge": "msedge.exe", "microsoft edge": "msedge.exe", "age": "msedge.exe",
        "ed": "msedge.exe", "ege": "msedge.exe",
        "google": "chrome.exe", "chrome": "chrome.exe",
        "notepad": "notepad.exe", "calculator": "calculator.exe",
        "spotify": "Spotify.exe", "code": "code.exe", "vscode": "code.exe",
        "explorer": "explorer.exe", "file explorer": "explorer.exe",
        "word": "WINWORD.exe", "excel": "EXCEL.exe", "powerpoint": "POWERPNT.exe",
    }
    proc = process_map.get(app_name.lower())
    if proc:
        os.system(f"taskkill /f /im {proc}")
    else:
        close_app(app_name, match_closest=False)

def play_on_youtube(song):
    pywhatkit.playonyt(song)

def take_screenshot():
    pyautogui.screenshot("screenshot.png")

def get_battery():
    """Return battery percentage and charging status."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "Plugged in" if battery.power_plugged else "On battery"
            return f"Battery at {percent}%. {plugged}."
        else:
            return "No battery detected."
    except ImportError:
        return "psutil not installed. Run 'pip install psutil'."
    except Exception as e:
        return f"Battery info error: {e}"