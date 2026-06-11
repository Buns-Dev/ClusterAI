import pyttsx3
import speech_recognition as sr
from config import MIC_INDEX, ENERGY_THRESHOLD, PAUSE_THRESHOLD, VOICE_RATE, VOICE_ID_INDEX

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[VOICE_ID_INDEX].id)
engine.setProperty('rate', VOICE_RATE)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command(timeout=5, phrase_time_limit=10):
    r = sr.Recognizer()
    with sr.Microphone(device_index=MIC_INDEX) as source:
        r.energy_threshold = ENERGY_THRESHOLD
        r.pause_threshold = PAUSE_THRESHOLD
        r.adjust_for_ambient_noise(source, duration=1.0)
        
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            query = r.recognize_google(audio, language='en-in')
            
            if len(query) < 2:
                return "none"
            return query.lower()
        except Exception:
            return "none"