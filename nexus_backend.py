import os
import time
import datetime
import threading
import json
import shared
import commands
import advanced_math
from llama_cpp import Llama

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
        
        # Initialize Voice Engines
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

        # NATIVE LOCAL LLM HUB SETUP (Path C Implementation)
        model_filename = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
        model_path = os.path.join(os.path.dirname(__file__), "models", model_filename)
        
        if os.path.exists(model_path):
            print(f"🧠 Loading ClusterAI Engine Weights into memory [{model_filename}]...")
            try:
                self.local_llm = Llama(
                    model_path=model_path,
                    n_ctx=4096,   # High-efficiency token window
                    n_threads=4,  # Safe core configuration for target execution
                    verbose=False # Suppress heavy console matrix outputs
                )
                print("🟢 ClusterAI Engine successfully loaded and online!")
            except Exception as e:
                print(f"❌ ERROR: Direct model initialization failed: {e}")
                self.local_llm = None
        else:
            print(f"❌ CRITICAL ERROR: Standalone model weight missing at {model_path}")
            self.local_llm = None

    def speak(self, text):
        """Pushes string components to the HUD frame queue and voice synthesis output."""
        shared.message_queue.put({"type": "speak", "text": text})
        if HAS_VOICE_LIBS and self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def speak_voice_only(self, text):
        """Processes audio generation parameters independently from layout canvas tracking."""
        if HAS_VOICE_LIBS and self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass

    def get_time_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12: return "Good morning"
        if hour < 18: return "Good afternoon"
        return "Good evening"

    def query_local_llm(self, query):
        """Routes conversational requests to the native standalone Llama context matrix using Chat formats."""
        if self.local_llm is None:
            return {
                "ui": "⚠️ LOCAL CORE LINK FAULT\nNative weight file not detected inside /models/. Verify local directory layout.",
                "voice": "Connection to my local intelligence engine failed. Please verify that the model file is placed in the models directory."
            }

        try:
            # Use the built-in Chat Completion wrapper to handle Llama 3.2 specific tokens automatically
            output = self.local_llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are ClusterAI, a highly optimized desktop intelligence matrix. Provide brief, elegant, smart, and direct answers. Avoid lengthy walls of text."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=2048,
                stop=["<|eot_id|>", "<|end_of_text|>"]
            )
            
            # Extract only the clean message content
            response_text = output['choices'][0]['message']['content'].strip()
            
            return {
                "ui": f"🌌 NEURAL MATRIX STREAM :: GENERATION LINK\n"
                      f"———————————————————————————————————————————————————————\n"
                      f"{response_text}\n"
                      f"———————————————————————————————————————————————————————\n"
                      f"📡 Native localized stream finalized successfully.",
                "voice": response_text
            }
        except Exception as e:
            return {
                "ui": f"⚠️ INTERNAL LINK GENERATION EXCEPTION\nHardware layer evaluation issue: {str(e)}",
                "voice": "An error occurred inside my execution layer while calculating an inference output."
            }

    def process_query_logic(self, query):
        """Orchestrator prioritizing Math Matrix -> Rigid Tools -> LLM Fallback (Nexus Only)."""
        clean = query.strip().lower()
        
        # 1. Advanced Math Intercept
        if any(t in clean for t in ["integrate", "integral", "calculus", "differentiate", "derivative", "solve", "simplify"]):
            math_res = advanced_math.process_math_query(clean)
            if math_res:
                return math_res
                
        # 2. Hardcoded Tool Execution
        tool_res = commands.process_command(query)
        if tool_res is not None:
            return tool_res
            
        # 3. Dynamic Local LLM Processing Gateway (Synapse is Bypassed)
        return self.query_local_llm(query)

    def ambient_wake_word_loop(self):
        """Monitors command pipes across asynchronous thread nodes."""
        while self.is_running:
            if self.interaction_mode == "text":
                try:
                    cmd = shared.command_queue.get_nowait()
                    if cmd == "/voice_capture_intent":
                        self.activate_voice_sequence()
                    else:
                        shared.message_queue.put({"type": "listen", "text": cmd})
                        reply = self.process_query_logic(cmd)
                        
                        if isinstance(reply, dict):
                            shared.message_queue.put({"type": "speak", "text": reply["ui"]})
                            threading.Thread(target=self.speak_voice_only, args=(reply["voice"],), daemon=True).start()
                        else:
                            self.speak(reply)
                except Exception:
                    pass

            elif self.interaction_mode == "voice":
                if HAS_VOICE_LIBS:
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
                else:
                    self.interaction_mode = "text"
                
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
    print("ClusterAI Backend Engine Framework Initializing...")
    start_backend_engine()
    while True:
        time.sleep(1)