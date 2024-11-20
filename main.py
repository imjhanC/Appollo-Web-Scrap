import tkinter as tk
from tkinter import Tk, ttk
from tkinter import messagebox
import undetected_chromedriver as uc

# This is a GUI for login into APPOLLO.io , SSM , Linkedin , SSM 
def login_gui():
    root = tk.Tk()
    root.title("App's title")
    window_width = 800   # Set Window width HERE
    window_height = 400   # Set Window height HERE

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight() 

    # Calculate the position to center the window
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")  # Set window dimensions
    root.resizable(True, True) # change back to FALSE when everything is done 
    root.mainloop()

if __name__ == "__main__":
    login_gui()