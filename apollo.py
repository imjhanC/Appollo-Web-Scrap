import tkinter as tk
from tkinter import Toplevel, ttk
from tkinter import messagebox
import sys
import json
import os
import re
import threading
import time 
import pickle
from PIL import Image, ImageTk 
import tkinter.font as tkfont
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException , StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException, WebDriverException, ElementClickInterceptedException
from tkinter import Tk, Text, Button, BOTH, LEFT, RIGHT, Y, END, VERTICAL, HORIZONTAL
from selenium.webdriver.support.expected_conditions import staleness_of

# This is the class for display how many seconds left for the user to enter the 2FA code via authenticator (multithreading)
class TwoFactorCountdown:
    def __init__(self, count):
        self.root = None
        self.count = count
        self.label_prefix = None
        self.label_count = None
        
    def create_countdown_window(self):
        # Ensure this runs in the main thread
        self.root = tk.Tk()
        self.root.title("Microsoft 2FA Countdown Timer")
        self.root.wm_attributes("-topmost", 1)
        self.root.geometry("300x100")
        
        frame = tk.Frame(self.root)
        frame.pack(pady=20)
        
        self.label_prefix = tk.Label(frame, text="Time left for 2FA:", font=("Arial", 12))
        self.label_prefix.grid(row=0, column=0)
        
        self.label_count = tk.Label(frame, text=f"{self.count} seconds", fg="red", font=("Arial", 14))
        self.label_count.grid(row=0, column=1)
        
        self.update_countdown()
        
    def update_countdown(self):
        if self.count > 0:
            self.label_count.config(text=f"{self.count} seconds", fg="red")
            self.count -= 1
            self.root.after(1000, self.update_countdown)
        else:
            self.label_prefix.config(text="")
            self.label_count.config(text="Time is up!", fg="black")
            self.root.after(2000, self.root.destroy)  # Close after 2 seconds
    
    def start(self):
        # Use Queue.Queue or threading.Event for thread-safe communication if needed
        self.create_countdown_window()
        self.root.mainloop()

# This is the GUI for user to enter their desired LEADS before inserting into apollo.io
def select_details_gui():
    job_titles_value = []
    location_value = []
    industry_value = []

    previous_text1 = ""
    previous_text2 = ""
    previous_text3 = ""


    def reload_dropdowns():
        """Reload all dropdown values from their respective files"""
        global job_titles_dropdown, location_dropdown, industries_dropdown
        
        # Read updated values from files
        job_titles = read_file("jobtitle.txt")
        locations = read_file("location.txt")
        industries = read_file("industry.txt")
        
        # Update dropdown values
        job_titles_dropdown['values'] = job_titles
        location_dropdown['values'] = locations
        industries_dropdown['values'] = industries
        
        # Clear current selections
        job_titles_dropdown.set('')
        location_dropdown.set('')
        industries_dropdown.set('')

    def setting():
    # Function to handle the opening of the industry section
        def on_industry_click():
            # Remove any existing widgets before creating a new one
            for widget in text_frame.winfo_children():
                widget.destroy()

            # Create a label for "Industry"
            label_industry = ttk.Label(text_frame, text="Edit / Add Industry:", font=("Helvetica", 10, "bold"))
            label_industry.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Create a Text widget for displaying/editing industry content
            text_industry = Text(text_frame, width=50, height=15, wrap="word")
            text_industry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

            # Add a scrollbar for the Text widget
            scrollbar_industry = ttk.Scrollbar(text_frame, orient="vertical", command=text_industry.yview)
            scrollbar_industry.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
            text_industry.config(yscrollcommand=scrollbar_industry.set)

            # Add an Entry widget to add a new industry
            entry_industry = ttk.Entry(text_frame, width=62)
            entry_industry.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            # Placeholder text for entry_industry
            placeholder_industry = "Enter new industry here..."

            def on_focus_in_industry(event):
                if entry_industry.get() == placeholder_industry:
                    entry_industry.delete(0, END)  # Clear placeholder text
                    entry_industry.config(foreground="black")

            def on_focus_out_industry(event):
                if entry_industry.get() == "":
                    entry_industry.insert(0, placeholder_industry)
                    entry_industry.config(foreground="gray")

            # Set the placeholder text initially
            entry_industry.insert(0, placeholder_industry)
            entry_industry.config(foreground="gray")

            # Bind focus events to handle placeholder text
            entry_industry.bind("<FocusIn>", on_focus_in_industry)
            entry_industry.bind("<FocusOut>", on_focus_out_industry)

            # Save button for the new industry
            def save_new_industry():
                new_industry = entry_industry.get()
                if new_industry and new_industry != placeholder_industry:
                    # Append to the industry.txt file
                    with open("industry.txt", "a") as file:
                        file.write(new_industry + "\n")
                    # Clear the entry widget and reload content
                    entry_industry.delete(0, END)
                    load_industry()  # Reload the industry content to reflect the new addition

            # Save button for the content of Text widget (Industry)
            def save_industry():
                content = text_industry.get("1.0", "end-1c")  # Get the content from the Text widget
                with open("industry.txt", "w") as file:
                    file.write(content)  # Write the content to the file
                load_industry()  # Reload content after saving

            # Clear button for the entry field
            def clear_industry_entry():
                entry_industry.delete(0, END)

            def save_combined():
                save_new_industry()
                save_industry()

            save_button = ttk.Button(text_frame, text="Save", command=save_combined)
            save_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            clear_button = ttk.Button(text_frame, text="Clear", command=clear_industry_entry)
            clear_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

            # Refresh button to reload the content
            def load_industry():
                try:
                    with open("industry.txt", "r") as file:
                        content = file.read()
                        text_industry.delete("1.0", "end")  # Clear any existing content
                        text_industry.insert("1.0", content)
                except FileNotFoundError:
                    text_industry.delete("1.0", "end")
                    text_industry.insert("1.0", "industry.txt file not found.")

            load_industry()  # Load content initially


        # Function to handle the opening of the job title section
        def on_jobtitle_click():
            # Remove any existing widgets before creating a new one
            for widget in text_frame.winfo_children():
                widget.destroy()

            # Create a label for "Job Title"
            label_jobtitle = ttk.Label(text_frame, text="Edit / Add Job Title:", font=("Helvetica", 10, "bold"))
            label_jobtitle.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Create a Text widget for displaying/editing job title content
            text_jobtitle = Text(text_frame, width=50, height=15, wrap="word")
            text_jobtitle.grid(row=1, column=0, padx=10, pady=10, sticky="w")

            # Add a scrollbar for the Text widget
            scrollbar_jobtitle = ttk.Scrollbar(text_frame, orient="vertical", command=text_jobtitle.yview)
            scrollbar_jobtitle.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
            text_jobtitle.config(yscrollcommand=scrollbar_jobtitle.set)

            # Add an Entry widget to add a new job title
            entry_jobtitle = ttk.Entry(text_frame, width=62)
            entry_jobtitle.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            # Placeholder text for entry_jobtitle
            placeholder_jobtitle = "Enter new job title here..."

            def on_focus_in_jobtitle(event):
                if entry_jobtitle.get() == placeholder_jobtitle:
                    entry_jobtitle.delete(0, END)  # Clear placeholder text
                    entry_jobtitle.config(foreground="black")

            def on_focus_out_jobtitle(event):
                if entry_jobtitle.get() == "":
                    entry_jobtitle.insert(0, placeholder_jobtitle)
                    entry_jobtitle.config(foreground="gray")

            # Set the placeholder text initially
            entry_jobtitle.insert(0, placeholder_jobtitle)
            entry_jobtitle.config(foreground="gray")

            # Bind focus events to handle placeholder text
            entry_jobtitle.bind("<FocusIn>", on_focus_in_jobtitle)
            entry_jobtitle.bind("<FocusOut>", on_focus_out_jobtitle)

            # Save button for the new job title
            def save_new_jobtitle():
                new_jobtitle = entry_jobtitle.get()
                if new_jobtitle and new_jobtitle != placeholder_jobtitle:
                    # Append to the jobtitle.txt file
                    with open("jobtitle.txt", "a") as file:
                        file.write(new_jobtitle + "\n")
                    # Clear the entry widget and reload content
                    entry_jobtitle.delete(0, END)
                    load_jobtitle()  # Reload the job title content to reflect the new addition

            # Save button for the content of Text widget (Job Title)
            def save_jobtitle():
                content = text_jobtitle.get("1.0", "end-1c")  # Get the content from the Text widget
                with open("jobtitle.txt", "w") as file:
                    file.write(content)  # Write the content to the file
                load_jobtitle()  # Reload content after saving

            # Clear button for the entry field
            def clear_jobtitle_entry():
                entry_jobtitle.delete(0, END)

            def save_combined():
                save_new_jobtitle()
                save_jobtitle()

            save_button = ttk.Button(text_frame, text="Save", command=save_combined)
            save_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            clear_button = ttk.Button(text_frame, text="Clear", command=clear_jobtitle_entry)
            clear_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

            # Refresh button to reload the content
            def load_jobtitle():
                try:
                    with open("jobtitle.txt", "r") as file:
                        content = file.read()
                        text_jobtitle.delete("1.0", "end")  # Clear any existing content
                        text_jobtitle.insert("1.0", content)
                except FileNotFoundError:
                    text_jobtitle.delete("1.0", "end")
                    text_jobtitle.insert("1.0", "jobtitle.txt file not found.")

            load_jobtitle()  # Load content initially


        # Function to handle the opening of the location section
        def on_location_click():
            # Remove any existing widgets before creating a new one
            for widget in text_frame.winfo_children():
                widget.destroy()

            # Create a label for "Location"
            label_location = ttk.Label(text_frame, text="Edit / Add Location:", font=("Helvetica", 10, "bold"))
            label_location.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Create a Text widget for displaying/editing location content
            text_location = Text(text_frame, width=50, height=15, wrap="word")
            text_location.grid(row=1, column=0, padx=10, pady=10, sticky="w")

            # Add a scrollbar for the Text widget
            scrollbar_location = ttk.Scrollbar(text_frame, orient="vertical", command=text_location.yview)
            scrollbar_location.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
            text_location.config(yscrollcommand=scrollbar_location.set)

            # Add an Entry widget to add a new location
            entry_location = ttk.Entry(text_frame, width=62)
            entry_location.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            # Placeholder text for entry_location
            placeholder_location = "Enter new location here..."

            def on_focus_in_location(event):
                if entry_location.get() == placeholder_location:
                    entry_location.delete(0, END)  # Clear placeholder text
                    entry_location.config(foreground="black")

            def on_focus_out_location(event):
                if entry_location.get() == "":
                    entry_location.insert(0, placeholder_location)
                    entry_location.config(foreground="gray")

            # Set the placeholder text initially
            entry_location.insert(0, placeholder_location)
            entry_location.config(foreground="gray")

            # Bind focus events to handle placeholder text
            entry_location.bind("<FocusIn>", on_focus_in_location)
            entry_location.bind("<FocusOut>", on_focus_out_location)

            # Save button for the new location
            def save_new_location():
                new_location = entry_location.get()
                if new_location and new_location != placeholder_location:
                    # Append to the location.txt file
                    with open("location.txt", "a") as file:
                        file.write(new_location + "\n")
                    # Clear the entry widget and reload content
                    entry_location.delete(0, END)
                    load_location()  # Reload the location content to reflect the new addition

            # Save button for the content of Text widget (Location)
            def save_location():
                content = text_location.get("1.0", "end-1c")  # Get the content from the Text widget
                with open("location.txt", "w") as file:
                    file.write(content)  # Write the content to the file
                load_location()  # Reload content after saving

            # Clear button for the entry field
            def clear_location_entry():
                entry_location.delete(0, END)

            def save_combined():
                save_new_location()
                save_location()

            save_button = ttk.Button(text_frame, text="Save", command=save_combined)
            save_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            clear_button = ttk.Button(text_frame, text="Clear", command=clear_location_entry)
            clear_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

            # Refresh button to reload the content
            def load_location():
                try:
                    with open("location.txt", "r") as file:
                        content = file.read()
                        text_location.delete("1.0", "end")  # Clear any existing content
                        text_location.insert("1.0", content)
                except FileNotFoundError:
                    text_location.delete("1.0", "end")
                    text_location.insert("1.0", "location.txt file not found.")

            load_location()  # Load content initially

        root_setting = Toplevel(root)  # Create a new top-level window
        root_setting.title("Settings") 
        window_width = 1270
        window_height = 600
        screen_width = root_setting.winfo_screenwidth()  # Get screen width
        screen_height = root_setting.winfo_screenheight()  # Get screen height
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        root_setting.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        root_setting.resizable(False, False)
        root_setting.columnconfigure(0, weight=1)
        root_setting.rowconfigure(0, weight=1)
        root_setting.transient(root)  # Keep the window on top
        root_setting.grab_set()  # Prevent interaction with the parent window

        setting_frm = ttk.Frame(root_setting, padding=20)
        setting_frm.grid(row=0, column=0, sticky="nsew")

        # Create a separate frame for the Text widget
        text_frame = ttk.Frame(setting_frm)
        text_frame.grid(row=0, column=1, rowspan=3, padx=100, pady=10, sticky="nsew")

        # Industry Button
        industry_button = ttk.Button(setting_frm, text="Add industry", width=30, command=on_industry_click)
        industry_button.grid(row=0, column=0, pady=63, sticky="w")

        # Job Title Button
        jobtitle_button = ttk.Button(setting_frm, text="Add job title", width=30, command=on_jobtitle_click)
        jobtitle_button.grid(row=1, column=0, pady=63, sticky="w")

        # Location Button
        location_button = ttk.Button(setting_frm, text="Add location", width=30, command=on_location_click)
        location_button.grid(row=2, column=0, pady=63, sticky="w")
        root_setting.protocol("WM_DELETE_WINDOW", lambda: [root_setting.destroy(), reload_dropdowns()])
        root_setting.mainloop()  # Start the event loop

    def add_to_textbox(textbox, dropdown):
        """Add the selected dropdown item to the textbox."""
        selected_item = dropdown.get()
        textbox_values = textbox.get("1.0", "end-1c").strip()  
        
        if selected_item:
            if selected_item in textbox_values:
                print("Already in textbox")
            else:
                # Insert the selected item into the textbox with a comma and newline
                textbox.insert(END, f"{selected_item}\n")
                # Clear the dropdown selection
                dropdown.set("")
        else:
            print("No item selected from dropdown")

    def read_file(filename):
        """Read file contents and return as a list of strings."""
        try:
            with open(filename, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"File {filename} not found.")
            messagebox.showerror("File Not Found",f"File {filename} not found.")
            return []

    def confirm_window():
        nonlocal job_titles_value, location_value, industry_value
        if not job_titles_value or not location_value or not industry_value:
            messagebox.showwarning(
                "Warning",
                "Please make sure all fields are not empty."
            )
            return None
        
        job_string = "\n".join(job_titles_value)
        location_string = "\n".join(location_value)
        industry_string = "\n".join(industry_value)
    
        message = f"**Job Title** : \n{job_string}\n\n**Location** : \n{location_string}\n\n**Industry** : \n{industry_string}"

        # Display a messagebox with Yes and No buttons
        if messagebox.askyesno("Confirm Action", f"Do you want to proceed with the details below?\n\n{message}"):
            print("Job Titles:", job_titles_value)
            print("Locations:", location_value)
            print("Industries:", industry_value)
            root.quit()
            return (job_titles_value, location_value, industry_value)
        else:
            print("User clicked No")
            pass
            return None 

    def on_text_change(text_type):
        nonlocal location_value, industry_value, job_titles_value
        nonlocal previous_text1, previous_text2, previous_text3

        new_text1 = job_titles_textbox.get("1.0", "end-1c").strip()
        new_text2 = location_textbox.get("1.0", "end-1c").strip()
        new_text3 = industries_textbox.get("1.0", "end-1c").strip()

        if (new_text1 != previous_text1) or (new_text2 != previous_text2) or (new_text3 != previous_text3):
            if text_type == "Job Titles" and new_text1 != previous_text1:
                temp_list = [item.strip() for item in new_text1.split("\n") if item.strip()]
                job_titles_value = temp_list
                previous_text1 = new_text1
            elif text_type == "Location" and new_text2 != previous_text2:
                temp_list = [item.strip() for item in new_text2.split("\n") if item.strip()]
                location_value = temp_list
                previous_text2 = new_text2
            elif text_type == "Industries" and new_text3 != previous_text3:
                temp_list = [item.strip() for item in new_text3.split("\n") if item.strip()]
                industry_value = temp_list
                previous_text3 = new_text3
            else:
                print("Bug")
        
        # Reset the modified state to allow the event to fire again
        job_titles_textbox.edit_modified(False)
        location_textbox.edit_modified(False)
        industries_textbox.edit_modified(False) 

    root = Tk()
    # Configure window's height and width
    window_height = 600
    window_width = 1270
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root.resizable(False, False)
    root.attributes('-topmost',True)
    
    # Make the root window's grid expandable
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Use ttk.Frame with the correct import
    frm = ttk.Frame(root, padding=20)
    frm.grid(column=0, row=0, sticky="nsew")

    # Add labels
    ttk.Label(frm, text="Select Job Titles").grid(column=0, row=0, pady=0, padx=100, sticky="w")
    ttk.Label(frm, text="Select Location").grid(column=1, row=0, pady=0, padx=130, sticky="w")
    ttk.Label(frm, text="Select Industry & Keywords").grid(column=2, row=0, pady=0, padx=100, sticky="w")

    # Add textboxes with scrollbars
    # Job Titles
    job_titles_frame = ttk.Frame(frm)
    job_titles_frame.grid(row=1, column=0, sticky="w", padx=15, pady=5)
    job_titles_textbox = Text(job_titles_frame, width=30, height=4, wrap="word")
    job_titles_textbox.pack(side=LEFT, fill=BOTH, expand=True)
    job_titles_scrollbar = ttk.Scrollbar(job_titles_frame, orient=VERTICAL, command=job_titles_textbox.yview)
    job_titles_scrollbar.pack(side=RIGHT, fill=Y)
    job_titles_textbox.config(yscrollcommand=job_titles_scrollbar.set)

    # Location
    location_frame = ttk.Frame(frm)
    location_frame.grid(row=1, column=1, sticky="w", padx=25, pady=5)
    location_textbox = Text(location_frame, width=30, height=4, wrap="word")
    location_textbox.pack(side=LEFT, fill=BOTH, expand=True)
    location_scrollbar = ttk.Scrollbar(location_frame, orient=VERTICAL, command=location_textbox.yview)
    location_scrollbar.pack(side=RIGHT, fill=Y)
    location_textbox.config(yscrollcommand=location_scrollbar.set)

    # Industries
    industries_frame = ttk.Frame(frm)
    industries_frame.grid(row=1, column=2, sticky="w", padx=30, pady=5)
    industries_textbox = Text(industries_frame, width=30, height=4, wrap="word")
    industries_textbox.pack(side=LEFT, fill=BOTH, expand=True)
    industries_scrollbar = ttk.Scrollbar(industries_frame, orient=VERTICAL, command=industries_textbox.yview)
    industries_scrollbar.pack(side=RIGHT, fill=Y)
    industries_textbox.config(yscrollcommand=industries_scrollbar.set)

    # Bind the <<Modified>> event to detect changes in the Textbox, fires when there is a change
    previous_text1 = job_titles_textbox.get("1.0", "end-1c").strip()  
    previous_text2 = location_textbox.get("1.0", "end-1c").strip()  
    previous_text3 = industries_textbox.get("1.0", "end-1c").strip()  
    job_titles_textbox.bind("<<Modified>>", lambda event: on_text_change("Job Titles"))
    location_textbox.bind("<<Modified>>", lambda event: on_text_change("Location"))
    industries_textbox.bind("<<Modified>>", lambda event: on_text_change("Industries"))

    # Read dropdown options from files
    job_titles = read_file("jobtitle.txt")
    locations = read_file("location.txt")
    industries = read_file("industry.txt")

    # Add dropdown menus and buttons
    # Dropdown for Job Titles
    job_titles_dropdown = ttk.Combobox(frm, values=job_titles, state="readonly", width=29)
    job_titles_dropdown.grid(row=2, column=0, pady=10, padx=15, sticky="w")
    job_titles_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(job_titles_textbox, job_titles_dropdown))
    job_titles_add_button.grid(row=2, column=0, pady=10, padx=(280, 0), sticky="e")

    # Dropdown for Locations
    location_dropdown = ttk.Combobox(frm, values=locations, state="readonly", width=29)
    location_dropdown.grid(row=2, column=1, pady=10, padx=25, sticky="w")
    location_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(location_textbox, location_dropdown))
    location_add_button.grid(row=2, column=1, pady=10, padx=(290, 0), sticky="e")

    # Dropdown for Industries
    industries_dropdown = ttk.Combobox(frm, values=industries, state="readonly", width=29)
    industries_dropdown.grid(row=2, column=2, pady=10, padx=30, sticky="w")
    industries_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(industries_textbox, industries_dropdown))
    industries_add_button.grid(row=2, column=2, pady=10, padx=(300, 0), sticky="e")

    # Add a setting button to invoke Setting windows 
    setting_image = Image.open("setting.png")  # Load the image
    setting_image = setting_image.resize((40, 40))  # Resize the image (corrected line)
    setting_image_tk = ImageTk.PhotoImage(setting_image)  # Convert to Tkinter-compatible format

    setting_button = Button(root, image=setting_image_tk,command=setting)  # Create the button with the image
    setting_button.grid(row=3, column=2, pady=20, padx=20, sticky="se")  # Place the button


    result = None
    def combined_command():
        nonlocal result
        result = confirm_window()
        if result is not None:
            root.quit()

    # Confirm button after selecting values
    confirm_button = ttk.Button(root, text="Confirm", command=combined_command)
    confirm_button.grid(row=3, column=0, pady=10, padx=(600, 0), sticky="w")
    
    def on_closing():
        nonlocal result
        result = None
        root.quit()

    # Keep a reference to the image to prevent it from being garbage collected
    setting_button.image = setting_image_tk
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    root.destroy()

    return result
    
# This is the logic for interacting inside the apollo.io
def login_to_apollo(workemail, password, vtiger_email, vtiger_pass, num_leads):
    driver = None
    countdown = None 

    # Function to extract emails from the file and store them into a list
    def extract_emails_from_file(file_path):
        email_list = []
        try:
            with open(file_path, "r") as file:
                for line in file:
                    # Remove whitespace and add to the list if it's not empty
                    email = line.strip()
                    if email:
                        email_list.append(email)
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
        return email_list


    try:
        options = uc.ChromeOptions()
        options.add_argument("--start-minimized")  # Or remove if testing in non-headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")

        print("Initializing Chrome...")
        driver = uc.Chrome(options=options)

        print("Logging in...")
        driver.get('https://app.apollo.io/#/login')
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

        # Find and click the "Log In with Microsoft" button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Log In with Microsoft']/parent::button")))  
        login_button.click()
        
        # Microsoft Page part
        # Wait for and enter email
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='loginfmt']")))
        email_input.clear()  # Clear any pre-filled text
        email_input.send_keys(workemail)

        # Click "Next" button for email
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        submit_button.click()

        # Wait for and enter password
        password_input = wait.until(EC.presence_of_element_located((By.ID, "i0118")))
        password_input.send_keys(password)

        signin_element = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[5]/div/div/div/div/input")))
        signin_element.click()

        countdown = TwoFactorCountdown(15)
        threading.Thread(target=countdown.start, daemon=True).start()
        time.sleep(15) # This is for authentication via 2FA
        
        no_button = wait.until(EC.element_to_be_clickable((By.ID, "idBtn_Back")))
        no_button.click()

        people_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='zp_aoXyS' and contains(text(), 'People')]"))
        )
        people_element.click()
        
        received_text = select_details_gui()
        if received_text is not None:
            job_titles, locations, industries = received_text
            print("Debug")
            print("Job Titles:", job_titles)
            print("Locations:", locations)
            print("Industries:", industries)
            
            # Continue with the rest of the Apollo.io interaction
        else:
            print("No details selected or user cancelled.")

        # Industry & Keywords
        industry_element = WebDriverWait(driver,10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='main-app']/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]/div[9]/div/span/div[1]/span"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", industry_element)
        industry_element.click()
        placeholder_element_industries = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Select-placeholder"))
        )
        placeholder_element_industries.click()
        time.sleep(3)
        input_element_industries = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Select-input"))
        )
        input_element_industries.send_keys(industries)
        time.sleep(2)
        input_element_industries.send_keys(Keys.ENTER)
        industry_element = WebDriverWait(driver,10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='main-app']/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]/div[9]/div/span/div[1]/span"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", industry_element)
        industry_element.click()

        # Job title Input
        job_titles_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Job Titles']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", job_titles_element)
        job_titles_element.click()

        placeholder_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Select-placeholder"))
        )
        placeholder_element.click()  # Click the placeholder
        time.sleep(2)
        job_title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.Select-input"))
        )
        time.sleep(5)
        job_title_input.send_keys(job_titles)
        time.sleep(1)
        job_title_input.send_keys(Keys.RETURN)

        job_titles_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Job Titles']"))
        )
        job_titles_element.click()

        # Location Input
        location_element = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Location']"))
        )
        location_element.click()
        time.sleep(3)
        placeholder_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Select-placeholder"))
        )
        placeholder_element.click()
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Select-input"))
        )
        input_element.send_keys(locations)
        time.sleep(2)
        input_element.send_keys(Keys.RETURN)
        location_element = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Location']"))
        )
        location_element.click()

        # This is to hide the filter 
        hide_filters_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='zp_tZMYK' and text()='Hide Filters']"))
        )
        hide_filters_element.click()

        tracking_file = "tracking.txt"
        emails = extract_emails_from_file(tracking_file)
        emails_json = json.dumps(emails, indent=4)
        print("Extracted Emails in JSON Format:")
        print(emails_json)

        # Initialize the lead processing
        target_leads = int(num_leads)
        current_leads = 0
        page_num = 1

        while current_leads < target_leads:
            try:
                # Wait for the target div containing rows
                target_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "zp_tFLCQ"))
                )
                
                # Locate all rows within the container
                rows = target_div.find_elements(By.XPATH, "./div")

                print(f"Processing rows on Page {page_num}:")
                for i, row in enumerate(rows):
                    # Check if we've processed the desired number of leads
                    if current_leads >= target_leads:
                        break

                    # Locate all columns within the current row
                    columns = row.find_elements(By.XPATH, "./*")
                    
                    # Extract text from each column
                    row_data = [column.text for column in columns]
                    print(", ".join(row_data))  # Print full row data
                    
                    # Ensure there are enough columns to check the 4th one
                    if len(columns) < 4:
                        # If row is skipped, add 1 to continue searching for leads
                        continue
                    
                    # Extract text from the 4th column
                    fourth_column_text = columns[3].text.strip()
                    
                    # Check if the 4th column's text exists in emails_json
                    if fourth_column_text in emails:
                        print(f"Skipping row (Already processed): {', '.join(row_data)}")
                        continue
                    
                    if fourth_column_text == "Access email":
                        # Locate the "Access email" button for the current row
                        access_email_buttons = row.find_elements(
                            By.XPATH,
                            ".//button[contains(@class, 'zp_qe0Li') and .//span[text()='Access email']]"
                        )
                        if access_email_buttons:
                            # Click the button and wait for 5 seconds
                            access_email_buttons[0].click()
                            time.sleep(5)
                            
                            # Re-fetch the 4th column's text
                            columns = row.find_elements(By.XPATH, "./*")
                            if len(columns) >= 4:
                                fourth_column_text = columns[3].text.strip()
                                email_address = fourth_column_text.split('+')[0].strip()
                                # Save the updated text into tracking.txt
                                with open("tracking.txt", "a") as f:
                                    f.write(f"{email_address}\n")
                                
                                # Print the accepted row
                                print(f"Accepted row (Access email updated): {', '.join(row_data)} >>> Clicked email address: {fourth_column_text}")
                                # Uncomment and modify as needed:
                                # vtiger_login(driver, vtiger_email, vtiger_pass, fourth_column_text)
                                current_leads += 1
                        else:
                            # If there is no email address even if the Access email button is clicked, ignore and proceed to the next row 
                            continue
                    
                    elif fourth_column_text == "Save contact":
                        # Ignore this row and continue to the next
                        continue
                    
                    elif "@" in fourth_column_text:
                        email_address = fourth_column_text.split('+')[0].strip()
                        # Save email into tracking.txt
                        with open("tracking.txt", "a") as f:
                            f.write(f"{email_address}\n")
                        
                        # Print the accepted row
                        print(f"Accepted row (Email): {', '.join(row_data)}")
                        
                        # Uncomment and modify as needed:
                        # vtiger_login(driver, vtiger_email, vtiger_pass, fourth_column_text)
                        current_leads += 1
                    
                    elif fourth_column_text == "No email":
                        # Ignore this row and continue to the next
                        continue

                    # If there is nothing matching all 5 criteria then ignore 
                    else:
                        continue

                # Check if we need to go to the next page
                if current_leads < target_leads:
                    # Try to find and click the next page button
                    try:
                        next_page_button = driver.find_element(
                            By.XPATH, 
                            "//i[contains(@class, 'apollo-icon-chevron-arrow-right')]"
                        )
                        next_page_button.click()
                        time.sleep(3)  # Wait for the page to load
                        page_num += 1
                    except NoSuchElementException:
                        # No more pages available
                        print("Reached the last page. Cannot find more leads.")
                        break

            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                break

        # Print final lead processing summary
        print(f"\nLead Processing Summary:")
        print(f"Initial Leads Requested: {target_leads}")
        print(f"Leads Processed: {current_leads}")
        print(f"Total Pages Processed: {page_num}")
    except Exception as e:
        print(f"Error in login to Apollo part 1: {str(e)}")
    finally:
        time.sleep(1250)
        #if driver:
        #    driver.quit()

def vtiger_login(driver , vtiger_email , vtiger_pass,each_row_email):
    # Save the current window handle (original tab)
    original_tab = driver.current_window_handle
    driver.execute_script("window.open('https://crmaccess.vtiger.com/log-in/', '_blank');")
    time.sleep(2)  # Give some time for the tab to open
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
    print("\nVTiger Logging in...")
    print("Row by each row: " + each_row_email)
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    email_field.send_keys(vtiger_email)
    password_field.send_keys(vtiger_pass)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)
    # Switch back to the original tab
    #driver.close()
    driver.switch_to.window(original_tab)
    print("Switched back to the original tab.")
    

def ssm_login(driver, extract_company_name):
    driver.execute_script("window.open('https://www.ssm-einfo.my/', '_blank');")
    time.sleep(10000)
    return driver 

def on_submit(root):
    work_email = workemail_entry.get()
    password = password_entry.get()
    vtiger_email_entry = vtiger_email.get()
    vtiger_password_entry = vtiger_password.get()
    ssm_email_entry = ssm_email.get()
    ssm_password_entry = ssm_password.get()
    num =  num_leads.get() # Number of leads 

    if not work_email or not password:
        messagebox.showerror("Input error", "Please enter all fields !")
        return
    
    threading.Thread(target=login_to_apollo, args=(work_email,password,vtiger_email_entry,vtiger_password_entry,num)).start()
    root.destroy()

def apollo_login():
    def show_password(event, entry):
        """Show the password when the button is pressed."""
        entry.config(show="")  # Reveal the password

    def hide_password(event, entry):
        """Hide the password when the button is released."""
        entry.config(show="*")  # Mask the password

    root_apollo = tk.Tk()
    root_apollo.title("Enter Account Credentials")
    
    # Window size and positioning
    window_width = 900
    window_height = 600
    screen_width = root_apollo.winfo_screenwidth()
    screen_height = root_apollo.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2 
    root_apollo.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root_apollo.resizable(False, False)

    # Make the root window's grid expandable
    root_apollo.columnconfigure(0, weight=1)
    root_apollo.columnconfigure(1, weight=1)  # Larger weight for the second column (email/password fields)
    root_apollo.rowconfigure(0, weight=1)

    # Main frame
    frm = ttk.Frame(root_apollo, padding=20)
    frm.grid(column=0, row=0, sticky="nsew")

    bold_font = tkfont.Font(weight="bold")

    # Work email label and entry
    ttk.Label(frm, text="Apollo.io account credential", font=bold_font).grid(column=0, row=0, columnspan=2, pady=(0, 10), sticky="w")
    ttk.Label(frm, text="Apollo.io Work Email:").grid(column=0, row=1, sticky="w", padx=10, pady=5)
    global workemail_entry
    workemail_entry = ttk.Entry(frm, width=50)
    workemail_entry.grid(column=1, row=1, padx=10, pady=5, sticky="w")

    # Password label, entry, and eye button
    ttk.Label(frm, text="Apollo.io Password:").grid(column=0, row=2, sticky="w", padx=10)
    
    # Password entry
    global password_entry
    password_entry = ttk.Entry(frm, width=50, show="*")  # Password masked by default
    password_entry.grid(column=1, row=2, padx=10, pady=(15, 20), sticky="w")
    
    # Eye button for Apollo password
    eye_button_apollo = ttk.Button(frm, text="👁")
    eye_button_apollo.grid(column=2, row=2, pady=0, padx=5, sticky="w")
    eye_button_apollo.bind("<ButtonPress-1>", lambda event: show_password(event, password_entry))  # Show password
    eye_button_apollo.bind("<ButtonRelease-1>", lambda event: hide_password(event, password_entry))  # Hide password

    # VTiger Email and Password
    ttk.Label(frm, text="Linkedin account credential", font=bold_font).grid(column=0, row=3, columnspan=2, pady=(20, 10), sticky="w")
    ttk.Label(frm, text="VTiger Email:").grid(column=0, row=4, sticky="w", padx=10, pady=5)
    global vtiger_email
    vtiger_email = ttk.Entry(frm, width=50)
    vtiger_email.grid(column=1, row=4, padx=10, pady=5, sticky="w")
    
    ttk.Label(frm, text="VTiger Password:").grid(column=0, row=5, sticky="w", padx=10, pady=5)
    global vtiger_password
    vtiger_password = ttk.Entry(frm, width=50, show="*")
    vtiger_password.grid(column=1, row=5, padx=10, pady=(15, 20), sticky="w")

    # Eye button for Linkedin password
    eye_button_linkedin = ttk.Button(frm, text="👁")
    eye_button_linkedin.grid(column=2, row=5, padx=5, sticky="w")
    eye_button_linkedin.bind("<ButtonPress-1>", lambda event: show_password(event, vtiger_password))  # Show password
    eye_button_linkedin.bind("<ButtonRelease-1>", lambda event: hide_password(event, vtiger_password))  # Hide password
    
    # For SSM
    ttk.Label(frm, text="SSM account credential", font=bold_font).grid(column=0, row=6, columnspan=2, pady=(20, 10), sticky="w")
    ttk.Label(frm, text="SSM Email:").grid(column=0, row=7, sticky="w", padx=10, pady=5)
    global ssm_email
    ssm_email = ttk.Entry(frm, width=50)
    ssm_email.grid(column=1, row=7, padx=10, pady=5, sticky="w")
    
    ttk.Label(frm, text="SSM Password:").grid(column=0, row=8, sticky="w", padx=10, pady=5)
    global ssm_password
    ssm_password = ttk.Entry(frm, width=50, show="*")
    ssm_password.grid(column=1, row=8, padx=10, pady=(15,20), sticky="w")

    # Eye button for SSM password
    eye_button_ssm = ttk.Button(frm, text="👁")
    eye_button_ssm.grid(column=2, row=8, pady=5, padx=5, sticky="w")
    eye_button_ssm.bind("<ButtonPress-1>", lambda event: show_password(event, ssm_password))  # Show password
    eye_button_ssm.bind("<ButtonRelease-1>", lambda event: hide_password(event, ssm_password))  # Hide password
    
    ttk.Label(frm, text="Enter number of leads you want to search", font=bold_font).grid(column=0, row=9, columnspan=2, pady=(0,0), sticky="w")
    ttk.Label(frm, text="Number of lead(s):").grid(column=0,row=10, sticky="w", padx=10 ,pady=5)
    global num_leads
    num_leads = ttk.Entry(frm, width=50)
    num_leads.grid(column=1,row=10, padx=10, pady=(0,0), sticky="w")
    # Login button
    ttk.Button(frm, text="Login", command=lambda: on_submit(root_apollo)).grid(column=0, row=11, columnspan=3, pady=20)

    root_apollo.mainloop() 

if __name__ == "__main__":
    apollo_login()
