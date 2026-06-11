# shared.py – single source of truth for inter-process communication
import queue

message_queue = queue.Queue()
command_queue = queue.Queue()
voice_trigger_callback = None

# Tracks which LLM engine the user selected at launch
selected_model = "flash"

def init():
    global selected_model
    selected_model = "flash"