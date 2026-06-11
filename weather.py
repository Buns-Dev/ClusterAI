import requests
import re

def get_weather_simple(city="Karachi"):
    """Fetches real-time meteorological data and formats it for dual-channel UI/Voice output."""
    try:
        url = f"https://wttr.in/{city}?u&format=%C|%t|%h|%w"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200 and "|" in response.text:
            parts = response.text.strip().split("|")
            condition = parts[0]
            temp = parts[1]
            humidity = parts[2]
            wind = parts[3] if len(parts) > 3 else "N/A"
            
            if '°F' in temp:
                match = re.search(r'([+-]?\d+)°F', temp)
                if match:
                    f_temp = int(match.group(1))
                    c_temp = int((f_temp - 32) * 5/9)
                    temp = f"+{c_temp}°C" if c_temp > 0 else f"{c_temp}°C"
            
            ui_panel = (
                f"🛰️ METEOROLOGICAL DIAGNOSTIC MATRIX :: {city.upper()}\n"
                f"———————————————————————————————————————————————————————\n"
                f" 🌀 ENVIRONMENT :: {condition}\n"
                f" 🌡️ THERMAL TEMP :: {temp}\n"
                f" 💧 ATMOS HUMID :: {humidity}\n"
                f" 💨 WIND VECTOR  :: {wind}\n"
                f"———————————————————————————————————————————————————————\n"
                f"📡 Climatology telemetry synchronized successfully."
            )
            
            spoken_temp = temp.replace("+", "").replace("°C", " degrees Celsius")
            voice_phrase = f"The climate profile for {city} indicates {condition} conditions at {spoken_temp}."
            
            return {"ui": ui_panel, "voice": voice_phrase}
        else:
            return {
                "ui": f"⚠️ System warning: Grid coordinates for '{city}' are currently obscured.",
                "voice": f"Warning sir, grid coordinates for {city} are currently obscured."
            }
    except Exception:
        return {
            "ui": f"❌ Critical telemetry error: Weather subsystem handshake timeout for {city}.",
            "voice": "Critical weather telemetry error. Link handshake timeout."
        }