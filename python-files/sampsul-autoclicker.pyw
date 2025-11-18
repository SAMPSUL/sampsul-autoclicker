import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard

stop_event = threading.Event()
click_thread = None
hotkeys_listener = None

HOTKEY = '<f6>'

def parse_interval(hours, mins, secs, millis):
    try:
        h = int(hours.get())
        m = int(mins.get())
        s = int(secs.get())
        ms = int(millis.get())
    except ValueError:
        return None
    total = h*3600 + m*60 + s + ms/1000.0
    if total <= 0:
        return None
    return total

def click_loop(get_interval, button, click_type, repeat_count, repeat_forever, get_position):
    try:
        count = 0
        while not stop_event.is_set():
            interval = get_interval()
            if interval is None:
                break
            use_pick, px, py = get_position()
            if use_pick and px is not None and py is not None:
                if click_type == 'Single':
                    pyautogui.click(px, py, button=button)
                else:
                    pyautogui.doubleClick(px, py, button=button)
            else:
                if click_type == 'Single':
                    pyautogui.click(button=button)
                else:
                    pyautogui.doubleClick(button=button)
            count += 1
            if not repeat_forever and repeat_count is not None:
                if count >= repeat_count:
                    break
            wait_until = time.time() + interval
            while time.time() < wait_until:
                if stop_event.is_set():
                    break
                time.sleep(0.01)
    except Exception as e:
        try:
            messagebox.showerror("Error", f"An exception occurred:\n{e}")
        except:
            pass
    finally:
        on_thread_stopped()

root = tk.Tk()
root.title("sampsul autoclicker")
root.resizable(False, False)

try:
    root.iconbitmap("autoclickericon.ico")
except Exception:
    pass

mainframe = ttk.Frame(root, padding=12)
mainframe.grid(row=0, column=0, sticky="NSEW")

pad = 6

interval_frame = ttk.Labelframe(mainframe, text="Click interval")
interval_frame.grid(row=0, column=0, padx=pad, pady=pad, sticky="W")

hours_var = tk.StringVar(value="0")
mins_var = tk.StringVar(value="0")
secs_var = tk.StringVar(value="0")
millis_var = tk.StringVar(value="100")

ttk.Label(interval_frame, text="hours").grid(row=0, column=0)
ttk.Entry(interval_frame, width=5, textvariable=hours_var).grid(row=0, column=1)
ttk.Label(interval_frame, text="mins").grid(row=0, column=2)
ttk.Entry(interval_frame, width=5, textvariable=mins_var).grid(row=0, column=3)
ttk.Label(interval_frame, text="secs").grid(row=0, column=4)
ttk.Entry(interval_frame, width=5, textvariable=secs_var).grid(row=0, column=5)
ttk.Label(interval_frame, text="milliseconds").grid(row=0, column=6)
ttk.Entry(interval_frame, width=7, textvariable=millis_var).grid(row=0, column=7)

options_frame = ttk.Labelframe(mainframe, text="Click options")
options_frame.grid(row=1, column=0, padx=pad, pady=pad, sticky="W")

mouse_button_var = tk.StringVar(value="left")
ttk.Label(options_frame, text="Mouse button:").grid(row=0, column=0, sticky="W")
ttk.Combobox(options_frame, textvariable=mouse_button_var,
             values=["left", "right", "middle"], state="readonly", width=8).grid(row=0, column=1, padx=6)

click_type_var = tk.StringVar(value="Single")
ttk.Label(options_frame, text="Click type:").grid(row=1, column=0, sticky="W")
ttk.Combobox(options_frame, textvariable=click_type_var,
             values=["Single", "Double"], state="readonly", width=8).grid(row=1, column=1, padx=6)

repeat_frame = ttk.Labelframe(mainframe, text="Click repeat")
repeat_frame.grid(row=2, column=0, padx=pad, pady=pad, sticky="W")

repeat_mode_var = tk.StringVar(value="forever")
repeat_count_var = tk.StringVar(value="1")
ttk.Radiobutton(repeat_frame, text="Repeat", variable=repeat_mode_var, value="count").grid(row=0, column=0, sticky="W")
ttk.Entry(repeat_frame, width=6, textvariable=repeat_count_var).grid(row=0, column=1)
ttk.Radiobutton(repeat_frame, text="Repeat until stopped", variable=repeat_mode_var, value="forever").grid(row=1, column=0, sticky="W")

pos_frame = ttk.Labelframe(mainframe, text="Cursor position")
pos_frame.grid(row=3, column=0, padx=pad, pady=pad, sticky="W")

pos_var = tk.StringVar(value="current")
x_var = tk.StringVar(value="0")
y_var = tk.StringVar(value="0")

ttk.Radiobutton(pos_frame, text="Current location", variable=pos_var, value="current").grid(row=0, column=0, sticky="W")
ttk.Radiobutton(pos_frame, text="Pick location", variable=pos_var, value="pick").grid(row=1, column=0, sticky="W")
ttk.Label(pos_frame, text="X").grid(row=1, column=1)
ttk.Entry(pos_frame, width=6, textvariable=x_var).grid(row=1, column=2)
ttk.Label(pos_frame, text="Y").grid(row=1, column=3)
ttk.Entry(pos_frame, width=6, textvariable=y_var).grid(row=1, column=4)
pick_btn = ttk.Button(pos_frame, text="Pick location", width=12)
pick_btn.grid(row=1, column=5, padx=6)

control_frame = ttk.Frame(mainframe)
control_frame.grid(row=4, column=0, pady=(10,0), sticky="W")

start_btn = ttk.Button(control_frame, text="Start (F6)", width=16)
start_btn.grid(row=0, column=0, padx=6)
stop_btn = ttk.Button(control_frame, text="Stop (F6)", width=16, state="disabled")
stop_btn.grid(row=0, column=1, padx=6)
help_btn = ttk.Button(control_frame, text="Help >>")
help_btn.grid(row=0, column=2, padx=6)

status_var = tk.StringVar(value="Idle")
ttk.Label(mainframe, textvariable=status_var, relief="sunken", anchor="w", width=60).grid(row=5, column=0, pady=(8,0), sticky="W")

def get_interval_callable():
    return lambda: parse_interval(hours_var, mins_var, secs_var, millis_var)

def get_position_callable():
    def inner():
        if pos_var.get() == 'pick':
            try:
                return True, int(x_var.get()), int(y_var.get())
            except ValueError:
                return True, None, None
        else:
            return False, None, None
    return inner

def start_clicking():
    global click_thread
    if click_thread and click_thread.is_alive():
        return
    interval = parse_interval(hours_var, mins_var, secs_var, millis_var)
    if interval is None:
        messagebox.showwarning("Warning", "Please enter a valid interval (> 0).")
        return
    forever = repeat_mode_var.get() == 'forever'
    rc = None
    if not forever:
        try:
            rc = int(repeat_count_var.get())
            if rc < 1:
                messagebox.showwarning("Warning", "Repeat count must be >= 1.")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Invalid repeat count.")
            return
    stop_event.clear()
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    status_var.set("Running...")
    button = mouse_button_var.get()
    ctype = click_type_var.get()
    click_thread = threading.Thread(
        target=click_loop,
        args=(get_interval_callable(), button, ctype, rc, forever, get_position_callable()),
        daemon=True)
    click_thread.start()

def stop_clicking():
    stop_event.set()
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    status_var.set("Stopped")

def on_thread_stopped():
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    status_var.set("Idle")

def toggle_start_stop():
    if start_btn.instate(['!disabled']):
        root.after(0, start_clicking)
    else:
        root.after(0, stop_clicking)

def pick_location_action():
    messagebox.showinfo("Pick location", "The window will hide. Move the cursor to your desired spot and left-click. Then return here.")
    root.withdraw()
    pos = {}
    def on_click(x, y, button, pressed):
        if pressed:
            pos['x'], pos['y'] = int(x), int(y)
            return False
    from pynput import mouse
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
    root.deiconify()
    if 'x' in pos:
        x_var.set(str(pos['x']))
        y_var.set(str(pos['y']))
        pos_var.set('pick')

def help_action():
    msg = (
        "sampsul autoclicker\n\n"
        "- Set your click interval in hours, minutes, seconds, and milliseconds.\n"
        "- Choose the mouse button and click type.\n"
        "- Choose how many times to repeat, or repeat until stopped.\n"
        "- Use 'Pick location' to select a screen point.\n"
        "- Press F6 to start or stop.\n\n"
        "Use responsibly."
    )
    messagebox.showinfo("Help", msg)

start_btn.config(command=start_clicking)
stop_btn.config(command=stop_clicking)
pick_btn.config(command=pick_location_action)
help_btn.config(command=help_action)

def on_activate_f6():
    toggle_start_stop()

def start_hotkey_listener():
    global hotkeys_listener
    try:
        hotkeys_listener = keyboard.GlobalHotKeys({HOTKEY: on_activate_f6})
        hotkeys_listener.start()
    except Exception as e:
        print("Hotkey error:", e)

start_hotkey_listener()

def on_close():
    if messagebox.askokcancel("Quit", "Do you want to close the program?"):
        stop_event.set()
        try:
            if hotkeys_listener:
                hotkeys_listener.stop()
        except:
            pass
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
