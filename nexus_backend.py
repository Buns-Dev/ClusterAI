# nexus_backend.py – Voice Automation & Intent Routing Engine
import time
import datetime
import threading
import shared
import commands
import advanced_math

try:
    import speech_recognition as sr
    import pyttsx3
    HAS_VOICE_LIBS = True
except ImportError:
    HAS_VOICE_LIBS = False

class NexusCore:
    def __init__(self):
        self.interaction_mode = "text"  
        self.is_running = True
        
        if HAS_VOICE_LIBS:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            if len(voices) > 0:
                self.tts_engine.setProperty('voice', voices[0].id) 
            self.tts_engine.setProperty('rate', 175)
            self.recognizer = sr.Recognizer()
        else:
            self.tts_engine = None
            self.recognizer = None

    def speak(self, text):
        """Dispatches plain text to the HUD terminal and speaks it aloud."""
        shared.message_queue.put({"type": "speak", "text": text})
        if HAS_VOICE_LIBS and self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def speak_voice_only(self, text):
        """Speaks vocal tracking phrase aloud without duplicating text in the UI panel."""
        if HAS_VOICE_LIBS and self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def get_time_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12: return "Good morning sir"
        elif hour < 18: return "Good afternoon sir"
        else: return "Good evening sir"

    def process_query_logic(self, query):
        """Intercepts specific system tasks or falls back to standard commands."""
        clean = query.strip().lower()
        
        # Intercept Advanced Mathematics Requests First
        if any(t in clean for t in ["integrate", "integral", "calculus", "differentiate", "derivative", "solve", "simplify"]):
            math_res = advanced_math.process_math_query(clean)
            if math_res:
                return math_res # Returns the dictionary layout safely
                
        # Baseline structural operations fall through to commands.py (Returns String)
        return commands.process_command(query)

    def ambient_wake_word_loop(self):
        """Orchestrates system processes safely via structured type handling."""
        while self.is_running:
            if self.interaction_mode == "text":
                try:
                    cmd = shared.command_queue.get_nowait()
                    if cmd == "/voice_capture_intent":
                        self.activate_voice_sequence()
                    else:
                        shared.message_queue.put({"type": "listen", "text": cmd})
                        reply = self.process_query_logic(cmd)
                        
                        # 🛠️ CRITICAL FIX: Safe Type Router to prevent Thread Crashes
                        if isinstance(reply, dict):
                            shared.message_queue.put({"type": "speak", "text": reply["ui"]})
                            threading.Thread(target=self.speak_voice_only, args=(reply["voice"],), daemon=True).start()
                        else:
                            self.speak(reply)
                except Exception:
                    pass

            elif self.interaction_mode == "voice":
                # Voice mode capture handling fallback pipeline
                from voice import take_command
                user_speech = take_command()
                if user_speech != "none":
                    shared.message_queue.put({"type": "listen", "text": user_speech})
                    
                    if "lets chat" in user_speech or "let's chat" in user_speech:
                        self.interaction_mode = "text"
                        shared.message_queue.put({"type": "system", "text": "🗪 Text Routing Engaged. Speech engine muted."})
                        self.speak("Switching protocol to chat interface input.")
                    else:
                        reply = self.process_query_logic(user_speech)
                        
                        if isinstance(reply, dict):
                            shared.message_queue.put({"type": "speak", "text": reply["ui"]})
                            self.speak_voice_only(reply["voice"])
                        else:
                            self.speak(reply)
                
            time.sleep(0.05)

    def activate_voice_sequence(self):
        self.interaction_mode = "voice"
        shared.message_queue.put({"type": "system", "text": "🎙️ Full Voice Link Active. Streaming Speech Integration."})
        greeting = f"{self.get_time_greeting()}, what should I do for you?"
        self.speak(greeting)

def start_backend_engine():
    core = NexusCore()
    backend_thread = threading.Thread(target=core.ambient_wake_word_loop, daemon=True)
    backend_thread.start()

if __name__ == "__main__":
    shared.init()
    print("Nexus Core Engine Backend Activated...")
    start_backend_engine()
    while True:
        time.sleep(1)