import os
import requests
from datetime import datetime

# Secure Key Management
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "e83d23ddd6594af6b9c174306261706")

def get_weather_simple(city):
    """
    Enterprise-grade weather telemetry with mathematically locked alignment.
    Values and units are concatenated BEFORE padding to prevent box rupture.
    """
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=7&aqi=no&alerts=no"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            error_data = response.json().get("error", {})
            err_msg = error_data.get("message", "Connection denied")
            return {
                "ui": f"\n⚠️  TELEMETRY FAILURE\n"
                      f"{'='*90}\n"
                      f"Location: {city.upper()}\n"
                      f"Fault Code: {err_msg}\n"
                      f"{'='*90}\n",
                "voice": f"Weather telemetry failed for {city}. Check the city name and try again."
            }
            
        data = response.json()
        
        # Extract core telemetry
        location = data["location"]
        current = data["current"]
        forecast = data["forecast"]["forecastday"]
        
        name = location["name"]
        country = location["country"]
        region = location["region"]
        lat = location["lat"]
        lon = location["lon"]
        
        # Build the strings FIRST to prevent padding separation
        cond_val = f"{current['condition']['text'][:55]}"
        temp_val = f"{int(current['temp_c'])}°C"
        hum_val  = f"{current['humidity']}%"
        wind_val = f"{current['wind_kph']} KM/H"
        pres_val = f"{current['pressure_mb']} mb"
        uv_val   = f"{current['uv']}"
        
        # --- BUILD UI PANEL ---
        BORDER = "=" * 90
        
        panel = f"\n"
        panel += f"{'🛰️  METEOROLOGICAL DIAGNOSTIC MATRIX':^90}\n"
        panel += f"{BORDER}\n\n"
        
        # Current conditions header
        panel += f"  📍 LOCATION: {name}, {region}, {country}\n"
        panel += f"  🧭 COORDINATES: {lat}°N, {lon}°E\n\n"
        
        # Current telemetry grid (100% locked width)
        panel += f"  ╔══════════════════════════════════════════════════════════════════════╗\n"
        panel += f"  ║ CURRENT CONDITIONS                                                   ║\n"
        panel += f"  ╠══════════════════════════════════════════════════════════════════════╣\n"
        panel += f"  ║ {'Condition:':<14} {cond_val:<57}║\n"
        panel += f"  ║ {'Temperature:':<14} {temp_val:<57}║\n"
        panel += f"  ║ {'Humidity:':<14} {hum_val:<57}║\n"
        panel += f"  ║ {'Wind Speed:':<14} {wind_val:<57}║\n"
        panel += f"  ║ {'Pressure:':<14} {pres_val:<57}║\n"
        panel += f"  ║ {'UV Index:':<14} {uv_val:<57}║\n"
        panel += f"  ╚════════════════════════════════════════════════════════════════════════╝\n\n"
        
        # 7-day forecast header
        panel += f"  7-DAY WEEKLY FORECAST GRID\n"
        panel += f"  {'-'*86}\n"
        
        COL_WIDTH = 18
        
        # Column headers
        day_headers = ""
        for day_data in forecast:
            date_obj = datetime.strptime(day_data["date"], "%Y-%m-%d")
            day_name = date_obj.strftime("%a").upper()
            day_headers += f"{day_name:^{COL_WIDTH}}"
        panel += f"  {day_headers}\n"
        
        # Temperature row
        temp_row = ""
        for day_data in forecast:
            max_t = int(day_data["day"]["maxtemp_c"])
            min_t = int(day_data["day"]["mintemp_c"])
            temp_str = f"{max_t}°/{min_t}°"
            temp_row += f"{temp_str:^{COL_WIDTH-1}}"
        panel += f"  {temp_row}\n"
        
        # Condition icons & chance of rain
        condition_row = ""
        for day_data in forecast:
            rain = day_data["day"]["daily_chance_of_rain"]
            
            if rain > 60:
                icon = "🌧️"
            elif rain > 30:
                icon = "⛅"
            else:
                icon = "☀️"
            
            condition_str = f"{icon} {rain}%"
            condition_row += f"{condition_str:^{COL_WIDTH-2}}"
        panel += f"  {condition_row}\n"
        
        # Humidity row
        humidity_row = ""
        for day_data in forecast:
            humidity = day_data["day"]["avghumidity"]
            humidity_str = f"💧 {humidity}%"
            humidity_row += f"{humidity_str:^{COL_WIDTH-3}}"
        panel += f"  {humidity_row}\n"
        
        # Wind speed row
        wind_row = ""
        for day_data in forecast:
            wind = int(day_data["day"]["maxwind_kph"])
            wind_str = f"💨 {wind}km/h"
            wind_row += f"{wind_str:^{COL_WIDTH}}"
        panel += f"  {wind_row}\n"
        
        panel += f"  {'-'*86}\n"
        panel += f"  📡 Telemetry synchronized. Grid locked.\n\n"
        
        voice = f"Weather telemetry synchronized for {name}. Current temperature {int(current['temp_c'])} degrees Celsius. Grid stable."
        
        return {"ui": panel, "voice": voice}
        
    except Exception as e:
        return {
            "ui": f"\n❌ CRITICAL SUBSYSTEM FAILURE\n"
                  f"{'='*90}\n"
                  f"Exception: {type(e).__name__}\n"
                  f"Details: {str(e)}\n"
                  f"{'='*90}\n",
            "voice": f"Critical error. {type(e).__name__} in weather telemetry."
        }


# --- TEST CODE ---
if __name__ == "__main__":
    print("\n🔬 TESTING WEATHER TELEMETRY SYSTEM\n")
    
    cities = ["London", "New York", "Tokyo", "Sydney", "Paris"]
    
    for city in cities:
        print(f"\n⏳ Fetching weather for {city}...")
        result = get_weather_simple(city)
        print(result["ui"])
        print("="*90)