import queue

message_queue = queue.Queue()
command_queue = queue.Queue()
voice_trigger_callback = None
selected_model = "flash"

def init():
    global selected_model
    selected_model = "flash"