import customtkinter as ctk
import tkinter as tk
import psutil
import queue
import datetime
import random
import os
import shared
from PIL import Image, ImageTk, ImageFilter, ImageDraw

BG_VOID = "#020205"
HUD_CYAN = "#00f0ff"
NOVA_MAGENTA = "#f900ff"
USER_BLUE = "#00a2ff"
USER_BG = "#0a0e14"
NOVA_BG = "#0d0a14"
TEXT_GLOW = "#e5e7eb"

app = None
chat_area, command_entry, status_label, bg_canvas, legend_frame = None, None, None, None, None
top_bar, bot_line, dock_frame = None, None, None
tracked_labels = []

engine_state = "orbit"
zoom_progress = 0.0
zoom_target = None
flash_glow_radius, think_glow_radius = 45, 45

bg_images_raw = {"flash": None, "nova": None}
master_orbs = {"flash": None, "nova": None}
cached_bg_photo = None
cached_orb_photos = {}

random.seed(1337)
stars_data = [(random.random(), random.random(), random.choice([1, 1, 1, 2, 2, 3]), 
               random.choice(["#ffffff", "#a5f3fc", "#38bdf8", "#c084fc", "#334155"])) for _ in range(260)]

def generate_master_orb(core_color, core_glow):
    def rgb(h): return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    c_rgb, g_rgb = rgb(core_color), rgb(core_glow)
    CENTER = 320
    base = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    glow1 = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    ImageDraw.Draw(glow1).ellipse([CENTER-220, CENTER-220, CENTER+220, CENTER+220], fill=g_rgb + (35,))
    base.alpha_composite(glow1.filter(ImageFilter.GaussianBlur(45)))
    glow2 = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    ImageDraw.Draw(glow2).ellipse([CENTER-140, CENTER-140, CENTER+140, CENTER+140], fill=c_rgb + (75,))
    base.alpha_composite(glow2.filter(ImageFilter.GaussianBlur(25)))
    ball = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    ImageDraw.Draw(ball).ellipse([CENTER-110, CENTER-110, CENTER+110, CENTER+110], fill=g_rgb + (240,))
    inner_light = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    ImageDraw.Draw(inner_light).ellipse([CENTER-85, CENTER-65, CENTER+85, CENTER+115], fill=c_rgb + (190,))
    mask = Image.new("L", (640, 640), 0)
    ImageDraw.Draw(mask).ellipse([CENTER-110, CENTER-110, CENTER+110, CENTER+110], fill=255)
    base.alpha_composite(Image.composite(inner_light.filter(ImageFilter.GaussianBlur(20)), ball, mask))
    return base

def load_assets():
    global bg_images_raw, master_orbs
    for m, c in [("flash", "#040d21"), ("nova", "#1a0421")]:
        try: bg_images_raw[m] = Image.open(f"{m}.jpeg" if m == "nova" else "flash_nebula.jpeg")
        except Exception: bg_images_raw[m] = Image.new('RGB', (1920, 1080), c)
    master_orbs["flash"] = generate_master_orb(HUD_CYAN, "#002b36")
    master_orbs["nova"] = generate_master_orb(NOVA_MAGENTA, "#20003b")

def redraw_space_canvas():
    global cached_bg_photo, cached_orb_photos
    if not bg_canvas: return
    w, h = bg_canvas.winfo_width(), bg_canvas.winfo_height()
    if w <= 10 or h <= 10: w, h = 800, 760
    bg_canvas.delete("all")
    cached_orb_photos = {}

    if engine_state == "active":
        target_img = bg_images_raw.get(shared.selected_model, bg_images_raw["flash"])
        if target_img:
            resized = target_img.resize((w, h), Image.Resampling.LANCZOS)
            cached_bg_photo = ImageTk.PhotoImage(resized.filter(ImageFilter.GaussianBlur(radius=25)))
            bg_canvas.create_image(0, 0, anchor="nw", image=cached_bg_photo)
        return
    
    for rx, ry, sz, color in stars_data:
        x, y = rx * w, ry * h
        if engine_state == "zooming":
            x += (x - (w / 2)) * zoom_progress * 2
            y += (y - (h / 2)) * zoom_progress * 2
        bg_canvas.create_oval(x, y, x + sz, y + sz, fill=color, outline=color)
        
    base_cx1, base_cy1, base_cx2, base_cy2 = w * 0.35, h * 0.45, w * 0.65, h * 0.45
    if engine_state == "zooming":
        tcx, tcy = (base_cx1, base_cy1) if zoom_target == "flash" else (base_cx2, base_cy2)
        cx1 = base_cx1 + ((w/2) - tcx) * zoom_progress
        cy1 = base_cy1 + ((h/2) - tcy) * zoom_progress
        cx2 = base_cx2 + ((w/2) - tcx) * zoom_progress
        cy2 = base_cy2 + ((h/2) - tcy) * zoom_progress
        f_scale = 1.0 + (zoom_progress * 15) if zoom_target == "flash" else 0.0
        t_scale = 1.0 + (zoom_progress * 15) if zoom_target == "nova" else 0.0
    else:
        cx1, cy1, cx2, cy2, f_scale, t_scale = base_cx1, base_cy1, base_cx2, base_cy2, 1.0, 1.0

    fd = int(240 * (f_scale if engine_state == "zooming" else (flash_glow_radius / 45.0)))
    td = int(240 * (t_scale if engine_state == "zooming" else (think_glow_radius / 45.0)))

    if f_scale > 0 and fd > 4:
        cached_orb_photos["flash"] = ImageTk.PhotoImage(master_orbs["flash"].resize((fd, fd), Image.Resampling.BILINEAR))
        bg_canvas.create_image(cx1, cy1, anchor="center", image=cached_orb_photos["flash"])
        if engine_state == "orbit": bg_canvas.create_text(cx1, cy1 + 75, text="✨ NEXUS ENGINE", font=("Consolas", 10, "bold"), fill=HUD_CYAN)

    if t_scale > 0 and td > 4:
        cached_orb_photos["nova"] = ImageTk.PhotoImage(master_orbs["nova"].resize((td, td), Image.Resampling.BILINEAR))
        bg_canvas.create_image(cx2, cy2, anchor="center", image=cached_orb_photos["nova"])
        if engine_state == "orbit": bg_canvas.create_text(cx2, cy2 + 75, text="🔮 SYNAPSE ENGINE", font=("Consolas", 10, "bold"), fill=NOVA_MAGENTA)

def do_zoom_animation():
    global zoom_progress
    zoom_progress += 0.04
    if zoom_progress >= 1.0: 
        zoom_progress = 1.0
        finalize_engine_launch()
    else: 
        redraw_space_canvas()
        app.after(16, do_zoom_animation)

def do_zoom_out_animation():
    global zoom_progress, engine_state
    zoom_progress -= 0.04
    if zoom_progress <= 0.0: 
        zoom_progress = 0.0
        engine_state = "orbit"
        legend_frame.place(relx=0.04, rely=0.84, anchor="w")
        redraw_space_canvas()
    else: 
        redraw_space_canvas()
        app.after(16, do_zoom_out_animation)

def on_canvas_motion(event):
    global flash_glow_radius, think_glow_radius
    if engine_state != "orbit": return
    w, h = bg_canvas.winfo_width(), bg_canvas.winfo_height()
    if w <= 10: return
    df = ((event.x - (w * 0.35)) ** 2 + (event.y - (h * 0.45)) ** 2) ** 0.5
    dt = ((event.x - (w * 0.65)) ** 2 + (event.y - (h * 0.45)) ** 2) ** 0.5
    f_r = 58 if df < 120 else 45
    t_r = 58 if dt < 120 else 45
    ch = (f_r != flash_glow_radius) or (t_r != think_glow_radius)
    flash_glow_radius, think_glow_radius = f_r, t_r
    bg_canvas.config(cursor="hand2" if (df < 120 or dt < 120) else "")
    if ch: redraw_space_canvas()

def on_canvas_click(event):
    global engine_state, zoom_target
    if engine_state != "orbit": return
    w, h = bg_canvas.winfo_width(), bg_canvas.winfo_height()
    if ((event.x - (w * 0.35)) ** 2 + (event.y - (h * 0.45)) ** 2) ** 0.5 < 120:
        bg_canvas.config(cursor="")
        legend_frame.place_forget()
        engine_state, zoom_target, shared.selected_model = "zooming", "flash", "flash"
        do_zoom_animation()
    elif ((event.x - (w * 0.65)) ** 2 + (event.y - (h * 0.45)) ** 2) ** 0.5 < 120:
        add_system_notification("⚠️ Synapse Engine: Core routing configuration required.")

def finalize_engine_launch():
    global engine_state
    engine_state = "active"
    redraw_space_canvas()
    top_bar.pack(fill="x", padx=15, pady=(15, 0))
    bot_line.pack(fill="x", padx=15, pady=(0, 10))
    chat_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    dock_frame.pack(fill="x", padx=15, pady=(0, 15))
    add_system_notification("⚡ Nexus Terminal Matrix Online. Active Passive Listening.")

def return_to_orbit():
    global engine_state, zoom_progress
    top_bar.pack_forget(); bot_line.pack_forget(); chat_area.pack_forget(); dock_frame.pack_forget()
    engine_state, zoom_progress = "zooming", 1.0
    do_zoom_out_animation()

def get_system_stats():
    return f"💻 CPU: {psutil.cpu_percent()}%  |  🧠 RAM: {psutil.virtual_memory().percent}%  |  💾 DISK: {psutil.disk_usage('/').percent}%"

def update_stats():
    if status_label: status_label.configure(text=get_system_stats())
    app.after(3000, update_stats)

def on_window_resize(event):
    if event.widget == app:
        dw = max(420, int(event.width * 0.65))
        for lbl in tracked_labels:
            try: lbl.configure(wraplength=dw)
            except: pass
        redraw_space_canvas()

def add_system_notification(text):
    row = ctk.CTkFrame(chat_area, fg_color="transparent")
    row.pack(fill="x", pady=6, padx=20)
    badge = ctk.CTkFrame(row, fg_color="#0a122c", corner_radius=12)
    badge.pack(anchor="center", ipadx=18, ipady=6)
    ctk.CTkLabel(badge, text=text.replace("=", ""), font=("Segoe UI Semibold", 11), text_color="#38bdf8").pack(anchor="center", padx=6)
    app.after(10, lambda: chat_area._parent_canvas.yview_moveto(1.0))

def add_message(speaker, text, is_user=False):
    row = ctk.CTkFrame(chat_area, fg_color="transparent")
    row.pack(fill="x", pady=10, padx=20)
    bubble = ctk.CTkFrame(row, fg_color=USER_BG if is_user else NOVA_BG, corner_radius=12, border_width=1, border_color="#1e293b")
    bubble.pack(side="right" if is_user else "left", ipadx=16, ipady=12)
    header = ctk.CTkFrame(bubble, fg_color="transparent", height=20)
    header.pack(fill="x", padx=2, pady=(0, 4))
    ctk.CTkLabel(header, text=speaker, font=("Segoe UI", 11, "bold"), text_color=USER_BLUE if is_user else NOVA_MAGENTA).pack(side="left")
    ctk.CTkLabel(header, text=datetime.datetime.now().strftime("%I:%M %p"), font=("Segoe UI", 9), text_color="#475569").pack(side="right", padx=(12, 0))
    lbl_text = ctk.CTkLabel(bubble, text=text if is_user else "", font=("Segoe UI", 13), text_color=TEXT_GLOW, justify="left", wraplength=max(420, int(app.winfo_width() * 0.65)))
    lbl_text.pack(anchor="w", padx=2, pady=(0, 2))
    tracked_labels.append(lbl_text)
    
    if not is_user:
        def type_effect(cl=0):
            if cl <= len(text): 
                lbl_text.configure(text=text[:cl])
                app.after(12, type_effect, cl + 1)
        type_effect()
    app.after(10, lambda: chat_area._parent_canvas.yview_moveto(1.0))

def update_ui():
    try:
        while True:
            msg = shared.message_queue.get_nowait()
            if msg["type"] == "speak": add_message("✦ NOVA", msg["text"], False)
            elif msg["type"] == "listen": add_message("⌨️ YOU" if "lets chat" in msg["text"].lower() else "🗣️ COMMAND", msg["text"], True)
            elif msg["type"] == "system": add_system_notification(msg["text"])
    except queue.Empty: pass
    app.after(50, update_ui)

def send_command(event=None):
    cmd = command_entry.get("1.0", tk.END).strip()
    if cmd: 
        shared.command_queue.put(cmd)
        command_entry.delete("1.0", tk.END)
    return "break"

def start_ui():
    global app, chat_area, command_entry, status_label, bg_canvas, legend_frame, top_bar, bot_line, dock_frame
    load_assets()
    app = ctk.CTk()
    app.title("NOVA Intelligence Suite")

    # ─── BULLETPROOF WINDOWS NATIVE TRAY INTERACTION ───
    icon_path = os.path.join(os.path.dirname(__file__), "star.ico")
    
    if os.path.exists(icon_path):
        try:
            # 1. Standard Tkinter pass for Window Title
            app.iconbitmap(icon_path)
            
            # 2. Direct Windows Win32 API Injection (Forces Taskbar Override)
            import ctypes
            
            # Load the icon file via Windows native engine
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            hicon = ctypes.windll.user32.LoadImageW(
                None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE
            )
            
            if hicon:
                app.update_idletasks() # Force OS window generation
                hwnd = ctypes.windll.user32.GetParent(app.winfo_id())
                
                WM_SETICON = 0x0080
                ICON_SMALL = 0
                ICON_BIG = 1
                
                # Push directly to Windows Taskbar System
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
        except Exception as e:
            print(f"HUD Alert: Windows API shortcut dropped: {e}")
    # ───────────────────────────────────────────────────

    app.geometry("900x760")
    app.minsize(620, 520)
    app.configure(fg_color=BG_VOID)
    app.bind("<Configure>", on_window_resize)

    bg_canvas = tk.Canvas(app, bg=BG_VOID, highlightthickness=0, borderwidth=0)
    bg_canvas.place(relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center")
    bg_canvas.bind("<Motion>", on_canvas_motion); bg_canvas.bind("<Button-1>", on_canvas_click)

    legend_frame = ctk.CTkFrame(app, fg_color="#020206", border_width=1, border_color="#111827", corner_radius=10)
    legend_frame.place(relx=0.04, rely=0.84, anchor="w")
    ctk.CTkLabel(legend_frame, text="SYSTEM MAP ROUTING DIRECTORY", font=("Segoe UI Semibold", 11, "bold"), text_color="#6b7280").pack(anchor="w", padx=14, pady=(12, 8))
    ctk.CTkLabel(legend_frame, text="● Link 01 -> Nexus Engine [ONLINE]", font=("Consolas", 11), text_color=HUD_CYAN).pack(anchor="w", padx=14, pady=2)
    ctk.CTkLabel(legend_frame, text="● Link 02 -> Synapse Engine [LOCKED]", font=("Consolas", 11), text_color=NOVA_MAGENTA).pack(anchor="w", padx=14, pady=(2, 12))

    top_bar = ctk.CTkFrame(app, fg_color="#000000", corner_radius=0, height=45, border_width=1, border_color=HUD_CYAN)
    
    # --- ADDED THE TOP-LEFT LOGO FIX HERE AS WELL ---
    logo_img = ctk.CTkImage(light_image=Image.open(icon_path), dark_image=Image.open(icon_path), size=(22, 22))
    ctk.CTkLabel(top_bar, image=logo_img, text="").pack(side="left", padx=(15, 5))
    # ------------------------------------------------
    
    ctk.CTkButton(top_bar, text="⏴ BACK", command=return_to_orbit, width=60, fg_color="transparent", hover_color="#111827", text_color=HUD_CYAN, font=("Segoe UI", 12, "bold")).pack(side="left", padx=(5, 5), pady=10)
    ctk.CTkLabel(top_bar, text="✦  N O V A", font=("Segoe UI Semibold", 14, "bold"), text_color=HUD_CYAN).pack(side="left", padx=10, pady=10)
    status_label = ctk.CTkLabel(top_bar, text=get_system_stats(), font=("Segoe UI", 11), text_color=HUD_CYAN)
    status_label.pack(side="right", padx=20, pady=10)

    bot_line = ctk.CTkFrame(app, fg_color=HUD_CYAN, height=1, corner_radius=0)
    chat_area = ctk.CTkScrollableFrame(app, fg_color="transparent")

    dock_frame = ctk.CTkFrame(app, fg_color="transparent")
    entry_container = ctk.CTkFrame(dock_frame, fg_color="#000000", corner_radius=12, border_width=1, border_color="#111827")
    entry_container.pack(side="left", fill="x", expand=True, ipady=2)
    
    command_entry = tk.Text(entry_container, height=2, wrap="word", bg="#000000", fg=TEXT_GLOW, insertbackground=HUD_CYAN, font=("Segoe UI", 13), relief="flat", borderwidth=0)
    command_entry.pack(fill="x", expand=True, padx=14, pady=8)
    command_entry.bind("<Return>", send_command)
    
    ctk.CTkButton(dock_frame, text=">", command=send_command, font=("Segoe UI", 15, "bold"), fg_color="#000000", hover_color="#090d16", text_color=USER_BLUE, width=50, height=46, corner_radius=12, border_width=1, border_color="#111827").pack(side="right", padx=(10, 0))
    ctk.CTkButton(dock_frame, text="🎤", command=lambda: shared.command_queue.put("/voice_capture_intent"), font=("Segoe UI", 14), fg_color="#000000", hover_color="#090d16", text_color=HUD_CYAN, width=50, height=46, corner_radius=12, border_width=1, border_color="#111827").pack(side="right", padx=(10, 0))

    app.after(100, redraw_space_canvas)
    app.after(150, update_stats)
    app.after(200, update_ui)
    app.mainloop()