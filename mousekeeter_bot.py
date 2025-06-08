"""Mousekeeter - A simple mouse clicker to keep your PC active by moving and right-clicking the mouse cursor periodically."""

__version__ = "1.0.0"

import pyautogui
import time
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import pystray
from PIL import Image
import sys

pyautogui.FAILSAFE = False

clicker_running = False
clicker_thread = None
tray_icon = None
app_hidden = False


def run_clicker(interval_seconds, total_duration_minutes):
    """Runs the mouse clicker in a separate thread.
    Args:
        interval_seconds (int): Interval in seconds between clicks.
        total_duration_minutes (int): Total duration in minutes for the clicker to run.
    """
    global clicker_running
    clicker_running = True

    end_time = datetime.now() + timedelta(minutes=total_duration_minutes)

    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    target_x1, target_y1 = 0, 0
    target_x2, target_y2 = screen_width - 1, screen_height - 1

    try:
        while datetime.now() < end_time and clicker_running:
            remaining = end_time - datetime.now()
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            label_status.config(text=f"Time left: {mins:02d}:{secs:02d}")
            app.update()

            pyautogui.moveTo(target_x1, target_y1, duration=0.5)
            pyautogui.moveTo(center_x, center_y, duration=0.5)
            pyautogui.click(button='right')
            pyautogui.moveTo(target_x2, target_y2, duration=0.5)

            for _ in range(interval_seconds):
                if not clicker_running:
                    break
                time.sleep(1)

        if clicker_running:
            messagebox.showinfo("Done", "Mousekeeter session complete.")
        label_status.config(text="Stopped.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
    finally:
        start_button.config(state="normal")
        stop_button.config(state="disabled")
        clicker_running = False

# ===== UI Actions =====


def start_clicker():
    """Starts the mouse clicker with user-defined interval and duration."""
    global clicker_thread
    try:
        interval = int(entry_interval.get() or "30")
        duration = int(entry_duration.get() or "10")

        start_button.config(state="disabled")
        stop_button.config(state="normal")
        label_status.config(text="Running...")

        clicker_thread = threading.Thread(
            target=run_clicker, args=(interval, duration), daemon=True)
        clicker_thread.start()
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")


def stop_clicker():
    """Stops the mouse clicker."""
    global clicker_running
    clicker_running = False
    label_status.config(text="Stopping...")


def minimize_to_tray():
    global tray_icon, app_hidden
    app.withdraw()
    app_hidden = True
    icon_image = Image.open("icon.ico")
    tray_icon = pystray.Icon("Mousekeeter", icon_image, "Mousekeeter", menu=pystray.Menu(
        pystray.MenuItem("Restore", restore_window),
        pystray.MenuItem("Quit", quit_app)
    ))
    threading.Thread(target=tray_icon.run, daemon=True).start()


def restore_window(icon=None, item=None):
    global app_hidden, tray_icon
    if app_hidden:
        app.deiconify()
        app_hidden = False
    if tray_icon:
        tray_icon.stop()


def quit_app(icon=None, item=None):
    stop_clicker()
    if tray_icon:
        tray_icon.stop()
    app.quit()
    sys.exit()


def on_close():
    minimize_to_tray()


app = tk.Tk()
app.title("Mousekeeter 🖱️")
app.geometry("320x260")
app.resizable(False, False)
app.iconbitmap("icon.ico")
app.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(app, text="Right-click Interval (seconds):").pack(pady=(20, 0))
entry_interval = tk.Entry(app, justify="center")
entry_interval.insert(0, "30")
entry_interval.pack()

tk.Label(app, text="Total Duration (minutes):").pack(pady=(10, 0))
entry_duration = tk.Entry(app, justify="center")
entry_duration.insert(0, "10")
entry_duration.pack()

frame_buttons = tk.Frame(app)
frame_buttons.pack(pady=15)

start_button = tk.Button(frame_buttons, text="Start",
                         width=10, bg="#4CAF50", fg="white", command=start_clicker)
start_button.pack(side="left", padx=5)

stop_button = tk.Button(frame_buttons, text="Stop", width=10,
                        bg="#f44336", fg="white", command=stop_clicker, state="disabled")
stop_button.pack(side="left", padx=5)

label_status = tk.Label(app, text="Ready.", font=("Arial", 11), fg="blue")
label_status.pack(pady=(10, 0))

tk.Label(app, text="🖱️ Keeps PC active\nby moving and clicking mouse.",
         font=("Arial", 9), justify="center").pack(pady=10)

app.mainloop()
