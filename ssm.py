import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import os
import threading
import time 
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException , StaleElementReferenceException

def login_to_ssm(username, password):
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--start-minimized')

        print("Initializing Chrome...")
        driver = uc.Chrome(options=options)

        print("Logging in...")
        driver.get('https://www.ssm-einfo.my/')
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

        # Find and click the "Login" button
        #login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()=' Login ']/parent::button")))  
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div/div/ul/li[2]/div/div/button[1]")))
        login_button.click()
        print("Click login")
        
        # Microsoft Page part
        # Wait for and enter email
        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.clear()  # Clear any pre-filled text
        username_input.send_keys(username)

        # Enter password
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

        # Wait until the login process completes or page is loaded
        time.sleep(1250) 
    except Exception as e:
            print(f"Error in login to SSM: {str(e)}")
    finally:
            try:
                if driver:
                    driver.quit()  # Ensure proper cleanup of the driver
            except Exception as e:
                print(f"Error during driver cleanup: {str(e)}")

    #return driver  # Return the driver object to interact further if necessary
    
def on_submit(root):
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Input error", "Please enter all fields !")
        return
    
    threading.Thread(target=login_to_ssm, args=(username,password)).start()
    root.destroy()

def ssm_login():
    def show_password(event):
        """Show the password when the button is pressed."""
        password_entry.config(show="")  # Reveal the password

    def hide_password(event):
        """Hide the password when the button is released."""
        password_entry.config(show="*")  # Mask the password

    root_ssm = tk.Tk()
    root_ssm.title("SSM login")
    
    # Window size and positioning
    window_width = 800
    window_height = 600
    screen_width = root_ssm.winfo_screenwidth()
    screen_height = root_ssm.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2 
    root_ssm.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root_ssm.resizable(True, True)

    # Make the root window's grid expandable
    root_ssm.columnconfigure(0, weight=1)
    root_ssm.rowconfigure(0, weight=1)

    # Main frame
    frm = ttk.Frame(root_ssm, padding=50)
    frm.grid(column=0, row=0, sticky="nsew")

    # Work email label and entry
    ttk.Label(frm, text="Work Email:").grid(column=0, row=0, pady=10, sticky="w")
    global username_entry
    username_entry = ttk.Entry(frm, width=50)
    username_entry.grid(column=1, row=0, pady=10)

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
    ttk.Button(frm, text="Login", command=lambda: on_submit(root_ssm)).grid(column=0, row=2, columnspan=3, pady=20)

    root_ssm.mainloop()

if __name__ == "__main__":
    ssm_login()
