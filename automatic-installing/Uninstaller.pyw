import os
import shutil
from tkinter import messagebox, Tk

PROGRAM_NAME = "Sampsul Autoclicker"

install_dir = os.path.join(os.environ["USERPROFILE"], "Desktop", "automatic-installing")

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
shortcut = os.path.join(desktop, f"{PROGRAM_NAME}.lnk")

if os.path.exists(shortcut):
    try:
        os.remove(shortcut)
    except Exception as e:
        print(f"Failed to remove shortcut: {e}")

if os.path.exists(install_dir):
    try:
        shutil.rmtree(install_dir)
    except Exception as e:
        print(f"Failed to remove install folder: {e}")

root = Tk()
root.withdraw() 
messagebox.showinfo("Uninstaller", f"{PROGRAM_NAME} has been removed successfully!")
root.destroy()
