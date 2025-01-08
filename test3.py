import tkinter as tk
from tkinter import Toplevel, ttk
from tkinter import messagebox
import tkinter.font as tkfont
from seleniumbase import SB 
import threading
import time
import json
import re
import pandas as pd
import os

class TwoFactorCountdown:
    def __init__(self):
        self.root = None
        self.continue_event = threading.Event()  # Event to signal when the button is clicked

    def create_continue_window(self):
        # Ensure this runs in the main thread
        self.root = tk.Tk()
        self.root.title("Click to continue")
        self.root.wm_attributes("-topmost", 1)
        self.root.geometry("300x100")
        
        # Add the "Continue" button
        continue_button = tk.Button(
            self.root, 
            text="Continue", 
            command=self.on_continue_button_clicked,
            font=("Arial", 12),
            fg="white", 
            bg="green",
            width=10
        )
        continue_button.pack(pady=30)

    def on_continue_button_clicked(self):
        # Signal the main thread to continue
        self.continue_event.set()
        self.root.destroy()  # Close the window

    def start(self):
        self.create_continue_window()
        self.root.mainloop()


def login_to_apollo():
    with SB(uc=True) as sb:
        sb.open('https://app.apollo.io/#/login')
        countdown = TwoFactorCountdown()
        threading.Thread(target=countdown.start, daemon=True).start()
        # Wait until the "Continue" button is clicked
        countdown.continue_event.wait()
        sb.wait_for_element('//span[@class="zp_tZMYK" and text()="Hide Filters"]', timeout=10)  # Wait for 10 seconds
        sb.click('//span[@class="zp_tZMYK" and text()="Hide Filters"]')  # Click the element
        sb.wait_for_element('#main-app > div.zp_iqUL3 > div > div.zp_ANgUY > div > div > div > div.zp_ajhD0 > div.zp_p234g.zp_B0KRZ > div.zp_pxYrj > div > div.zp_DhjQ0.zp_a7xaB > div > div.zp_d95ww > div.zp_A9IZq.zp_lRW3i > div.zp_tFLCQ')
        
        # Locate the table rows inside the specific div
        sb.wait_for_element('.zp_tFLCQ')  # Wait for the div with class "zp_tFLCQ" to be present
        
        # Locate all rows within the container
        rows = sb.find_elements('.zp_tFLCQ > div')  # Select all child divs as rows

        # Print the page number (optional, if you need to track pages)
        page_num = 1  # Change this as necessary based on your pagination logic
        print(f"Processing rows on Page {page_num}:")

        successful_leads = 0
        target_leads = 10  # Set your target number of leads to process

        for i, row in enumerate(rows):
            # Check if we've processed the desired number of leads
            if successful_leads >= target_leads:
                break

            # Locate all columns within the current row (assuming columns are direct children of row)
            columns = row.find_elements('xpath', './*')  # Use XPath to select all child elements

            # Extract the text from each column
            row_data = [column.text.strip() for column in columns]

            # Print the data for the current row
            print(f"Row {i + 1}: {row_data}")

            # Increment the successful leads count
            successful_leads += 1

login_to_apollo()