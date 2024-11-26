import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import os
import threading
import time 
from PIL import Image, ImageTk 
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException , StaleElementReferenceException

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

# This is the logic for interacting inside the apollo.io
def login_to_apollo(workemail, password):
    driver = None
    countdown = None 
    try:
        options = uc.ChromeOptions()
        options.add_argument('--start-minimized')

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
        
        # Job title Input
        job_titles_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Job Titles']"))
        )
        job_titles_element.click()

        placeholder_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Select-placeholder"))
        )
        placeholder_element.click()  # Click the placeholder
        job_title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.Select-input"))
        )
        test_jobtitle = "Software Engineer"   # The data input is HERE
        job_title_input.send_keys(test_jobtitle)
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
        placeholder_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Select-placeholder"))
        )
        placeholder_element.click()
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Select-input"))
        )
        location_text = "Selangor"
        input_element.send_keys(location_text)
        input_element.send_keys(Keys.RETURN)
        location_element = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Location']"))
        )
        location_element.click()

        #Industry & Keywords
        industry_keywords_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Industry & Keywords']"))
        )
        industry_keywords_element.click()
        placeholder_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Select-placeholder') and text()='Search industries...']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", placeholder_element)
        placeholder_element.click()  # Click the placeholder to focus the input field
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'Select-input')]"))
        )
        industry_text = "Electronics"
        input_element.send_keys(industry_text)
        input_element.send_keys(Keys.RETURN)
        industry_keywords_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Industry & Keywords']"))
        )
        industry_keywords_element.click()

        # This is to hide the filter 
        hide_filters_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='zp_tZMYK' and text()='Hide Filters']"))
        )
        hide_filters_element.click()

        time.sleep(1250) 

    except Exception as e:
        print(f"Error in login to Apollo part 1: {str(e)}")
        return None
    return driver  # Return the driver object to interact further if necessary
    
def on_submit(root):
    work_email = workemail_entry.get()
    password = password_entry.get()

    if not work_email or not password:
        messagebox.showerror("Input error", "Please enter all fields !")
        return
    
    threading.Thread(target=login_to_apollo, args=(work_email,password)).start()
    root.destroy()

def apollo_login():
    def show_password(event):
        """Show the password when the button is pressed."""
        password_entry.config(show="")  # Reveal the password

    def hide_password(event):
        """Hide the password when the button is released."""
        password_entry.config(show="*")  # Mask the password

    root_apollo = tk.Tk()
    root_apollo.title("Apollo.io login")
    
    # Window size and positioning
    window_width = 800
    window_height = 600
    screen_width = root_apollo.winfo_screenwidth()
    screen_height = root_apollo.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2 
    root_apollo.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root_apollo.resizable(True, True)

    # Make the root window's grid expandable
    root_apollo.columnconfigure(0, weight=1)
    root_apollo.rowconfigure(0, weight=1)

    # Main frame
    frm = ttk.Frame(root_apollo, padding=50)
    frm.grid(column=0, row=0, sticky="nsew")

    # Work email label and entry
    ttk.Label(frm, text="Work Email:").grid(column=0, row=0, pady=10, sticky="w")
    global workemail_entry
    workemail_entry = ttk.Entry(frm, width=50)
    workemail_entry.grid(column=1, row=0, pady=10)

    # Password label, entry, and eye button
    ttk.Label(frm, text="Password:").grid(column=0, row=1, pady=10, sticky="w")
    
    # Password entry
    global password_entry
    password_entry = ttk.Entry(frm, width=50, show="*")  # Password masked by default
    password_entry.grid(column=1, row=1, pady=10, sticky="w")

    # Eye button
    eye_button = ttk.Button(frm, text="👁")
    eye_button.grid(column=2, row=1, pady=5, padx=5, sticky="w")  # Place button next to password entry

    # Bind hold events to the eye button
    eye_button.bind("<ButtonPress-1>", show_password)  # Show password when button is pressed
    eye_button.bind("<ButtonRelease-1>", hide_password)  # Hide password when button is released

    # Buttons (e.g., Login)
    ttk.Button(frm, text="Login", command=lambda: on_submit(root_apollo)).grid(column=0, row=2, columnspan=3, pady=20)
    root_apollo.bind("<Return>", lambda event: on_submit(root_apollo))

    root_apollo.mainloop()

if __name__ == "__main__":
    apollo_login()
