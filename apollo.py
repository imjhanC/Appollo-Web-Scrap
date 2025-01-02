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
import tkinter.font as tkfont
import pandas as pd
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
from selenium import webdriver
from fake_useragent import UserAgent

# This is the class for display how many seconds left for the user to enter the 2FA code via authenticator (multithreading)
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

# This is the logic for interacting inside the apollo.io
def login_to_apollo(vtiger_email, vtiger_pass, num_leads):
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
        ua = UserAgent()
        options = uc.ChromeOptions()
        options.add_argument("--start-minimized")  # Or remove if testing in non-headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")
        #options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-popup-blocking')
        options.add_argument(f'--user-agent={ua.random}')
        print("Initializing Chrome...")
        driver = uc.Chrome(options=options)

        print("Logging in...")
        driver.get('https://app.apollo.io/#/login')
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        countdown = TwoFactorCountdown()
        threading.Thread(target=countdown.start, daemon=True).start()
        # Wait until the "Continue" button is clicked
        countdown.continue_event.wait()
    
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
        successful_leads = 0  # Track only successful lead processing
        page_num = 1
        all_leads = 0 # Track all row that has bot failed and successful leads

        while successful_leads < target_leads:
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
                    if successful_leads >= target_leads:
                        break

                    # Locate all columns within the current row
                    columns = row.find_elements(By.XPATH, "./*")
                    
                    # Extract text from each column
                    row_data = [column.text for column in columns]
                    row_data_processed = (", ".join(row_data))
                    print(f"Processing row: {', '.join(row_data)}")
                    
                    # Skip if not enough columns
                    if len(columns) < 4:
                        print("Skipping: Insufficient columns")
                        continue
                    
                    # Extract text from the 4th column
                    fourth_column = columns[3].text.strip()
                    fourth_column_text = re.sub(r'\+\d+', '', fourth_column).strip()
                    
                    # Skip if email already processed
                    if fourth_column_text in emails_json:
                        print(f"Skipping: Already processed - {fourth_column_text}")
                        all_leads += 1
                        row_counter = 0  # Initialize a counter outside the processing loop
                        # Process each row one at a time
                        with open("skipped_email.txt", "a") as f:
                            # Increment the row counter
                            row_counter += 1

                            # Split the row into columns
                            columns = row_data_processed.split(',')

                            # Apply cleaning logic for rows except row 5
                            if row_counter != 5:
                                # Check if the last column contains a '+' and a number
                                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                    columns[-1] = ""  # Remove the '+number' from the last column

                            # Rejoin the columns and write to the file
                            cleaned_row = ','.join(columns)
                            f.write(f"{cleaned_row}\n")
                        continue
                    
                    email_processed = False  # Flag to track if this row resulted in a successful lead
                    
                    # Handle "Access email" case
                    if fourth_column_text == "Access email":
                        # Original would be ".//button[contains(@class, 'zp_qe0Li') and .//span[text()='Access email']]" but it will click the Access phone button too ( Please be careful !!)
                        access_email_buttons = row.find_elements(
                            By.XPATH,
                            "//*[@id='table-row-0']/div[4]/div/span/button/span"  # Now it clicks the Access phone button only 
                        )
                        if access_email_buttons:
                            # Click the button and wait for 5 seconds
                            access_email_buttons[0].click()
                            time.sleep(5)
                            
                            # Re-fetch the 4th column's text
                            columns = row.find_elements(By.XPATH, "./*")
                            if len(columns) >= 4:
                                fourth_column = columns[3].text.strip()
                                fourth_column_text = re.sub(r'\+\d+', '', fourth_column).strip()
                                email_address = fourth_column_text.split('+')[0].strip()

                                if '@' in email_address and '.' in email_address:

                                    # Update row_data_processed with the new email address
                                    row_data = [column.text for column in columns]  # Get fresh data
                                    row_data[3] = email_address  # Update the email column
                                    row_data_processed = ", ".join(row_data)  # Recreate processed string

                                    with open("tracking.txt", "a") as f:
                                        f.write(f"{email_address}\n")
                                    
                                    print(f"Success: Access email updated - {email_address}")
                                    email_processed = vtiger_login(driver, vtiger_email, vtiger_pass, email_address, row_data_processed)
                                    all_leads += 1
                                else:
                                    # If even the Access email button is clicked , then there is no email (Skipping this row)
                                    all_leads += 1
                                    row_counter = 0  # Initialize a counter outside the processing loop
                                    # Process each row one at a time
                                    with open("rejected_leads.txt", "a") as f:
                                        # Increment the row counter
                                        row_counter += 1

                                        # Split the row into columns
                                        columns = row_data_processed.split(',')

                                        # Apply cleaning logic for rows except row 5
                                        if row_counter != 5:
                                            # Check if the last column contains a '+' and a number
                                            if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                                columns[-1] = ""  # Remove the '+number' from the last column

                                        # Rejoin the columns and write to the file
                                        cleaned_row = ','.join(columns)
                                        f.write(f"{cleaned_row}\n")
                                    continue
                        
                    # If the button is Save contact
                    elif fourth_column_text == "Save contact":
                        all_leads += 1
                        print(f"Skipping: Save contact button")
                        row_counter = 0  # Initialize a counter outside the processing loop
                        # Process each row one at a time
                        with open("rejected_leads.txt", "a") as f:
                            # Increment the row counter
                            row_counter += 1

                            # Split the row into columns
                            columns = row_data_processed.split(',')

                            # Apply cleaning logic for rows except row 5
                            if row_counter != 5:
                                # Check if the last column contains a '+' and a number
                                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                    columns[-1] = ""  # Remove the '+number' from the last column

                            # Rejoin the columns and write to the file
                            cleaned_row = ','.join(columns)
                            f.write(f"{cleaned_row}\n")
                        continue

                    # If the button is No email
                    elif fourth_column_text == "No email":
                        all_leads += 1
                        print(f"Skipping: No email button")
                        row_counter = 0  # Initialize a counter outside the processing loop
                        # Process each row one at a time
                        with open("rejected_leads.txt", "a") as f:
                            # Increment the row counter
                            row_counter += 1

                            # Split the row into columns
                            columns = row_data_processed.split(',')

                            # Apply cleaning logic for rows except row 5
                            if row_counter != 5:
                                # Check if the last column contains a '+' and a number
                                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                    columns[-1] = ""  # Remove the '+number' from the last column

                            # Rejoin the columns and write to the file
                            cleaned_row = ','.join(columns)
                            f.write(f"{cleaned_row}\n")
                        continue
                    
                    # Handle direct email case
                    elif "@" in fourth_column_text:
                        email_address = fourth_column_text.split('+')[0].strip()
                        with open("tracking.txt", "a") as f:
                            f.write(f"{email_address}\n")
                        
                        print(f"Success: Direct email - {email_address}")
                        email_processed = vtiger_login(driver, vtiger_email, vtiger_pass, email_address, row_data_processed)
                        all_leads += 1
                    
                    # Only increment successful_leads if we actually processed an email
                    if email_processed:
                        successful_leads += 1
                        print(f"Progress: {successful_leads}/{target_leads} Successful leads processed")

                # Check if we need to go to the next page
                if successful_leads < target_leads:
                    try:
                        next_page_button = driver.find_element(
                            By.XPATH, 
                            "//i[contains(@class, 'apollo-icon-chevron-arrow-right')]"
                        )
                        next_page_button.click()
                        time.sleep(3)  # Wait for the page to load
                        page_num += 1
                    except NoSuchElementException:
                        print("Reached the last page. Cannot find more leads.")
                        break

            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                break

        # Alert if we couldn't find enough leads
        if successful_leads < target_leads:
            print(f"Warning: Could only process {successful_leads} leads out of {target_leads} requested.")
    except Exception as e:
        print(f"Error in login to Apollo part 1: {str(e)}")
    finally:
        driver.quit()
        
        # Data Preprocessing
        result_leads_file = process_leads_file('leads.txt', 'leads.txt')
        print(f"Processing leads.txt: {'Successful' if result_leads_file else 'Failed'}")

        result_rejected_leads = process_leads_file('rejected_leads.txt','rejected_leads.txt')
        print(f"Processing rejected_leads.txt: {'Successful' if result_rejected_leads else 'Failed'}")

        result_rejected_leads_with_email = process_leads_file('rejected_leads_with_email.txt','rejected_leads_with_email.txt')
        print(f"Processing rejected_leads_with_email.txt: {'Successful' if result_rejected_leads_with_email else 'Failed'}")

        results_skipped_email = process_leads_file('skipped_email.txt','skipped_email.txt')
        print(f"Processing skipped_email.txt: {'Successful' if results_skipped_email else 'Failed'}")
    
        check_detail_company_name('leads.txt')
        txt_file_leads = 'leads.txt'
        excel_file_leads = 'leads.xlsx'

        txt_to_excel(txt_file_leads, excel_file_leads)
        txt_to_excel_rejected('rejected_leads.txt','rejected_leads.xlsx') 
        txt_to_excel_rejected('rejected_leads_with_email.txt','rejected_leads_with_email.xlsx')
        txt_to_excel_rejected('skipped_email.txt','skipped_email.xlsx')

        # Messagebox for notifying the user - Summary of the application
        message = (
            f"\nLead Processing Summary:\n"
            f"Target Leads (User Defined): {target_leads}\n"
            f"Successful Leads Processed: {successful_leads}\n"
            f"Skipped or Failed Leads Processed: {all_leads - successful_leads}\n"
            f"All Leads Processed: {all_leads}\n"
            f"Total Pages Processed: {page_num}"
        )

        # Display the messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        messagebox.showinfo("Lead Processing Summary", message)
        root.destroy()  # Properly destroy the tkinter root window

# This function is to transform textfile to excel file 
def txt_to_excel(txt_file, excel_file):
    try:
        # Try reading the file, handle inconsistent columns
        df = pd.read_csv(txt_file, sep=',', header=None, on_bad_lines='skip')  # Skip bad lines

        # Define headers manually (adjust if needed)
        headers = [
            'Name', 'Position', 'Company', 'Email', 'Phone',
            'City', 'Country', 'Extracted Company Name'
        ]

        # Check if the number of columns matches the headers
        if len(headers) != df.shape[1]:
            print(f"Warning: Adjusting headers to match the {df.shape[1]} columns in the text file.")
            headers = headers[:df.shape[1]]  # Truncate headers if there are fewer columns
            headers += [f"Column{i}" for i in range(len(headers), df.shape[1])]  # Add generic headers if needed

        # Assign headers to the DataFrame
        df.columns = headers

        # Clear and write the updated DataFrame to Excel
        df.to_excel(excel_file, index=False, engine='openpyxl')

        print(f"Successfully converted {txt_file} to {excel_file}, clearing old data and writing new data.")
    except Exception as e:
        print(f"An error occurred: {e}")

# This function is for transforming those rejected texfiles into excel file 
def txt_to_excel_rejected(txt_file, excel_file):
    try:
        # Check if the text file exists
        if not os.path.exists(txt_file):
            print(f"File {txt_file} does not exist. Skipping transformation.")
            return

        # Read the file and handle inconsistent columns
        df = pd.read_csv(txt_file, sep=',', header=None, on_bad_lines='skip')  # Skip bad lines

        # Define headers manually
        headers = [
            'Name', 'Position', 'Company', 'Email', 'Phone',
            'City', 'Country'
        ]

        # Check if the number of columns matches the headers
        if len(headers) != df.shape[1]:
            print(f"Warning: Adjusting headers to match the {df.shape[1]} columns in the text file.")
            headers = headers[:df.shape[1]]  # Truncate headers if there are fewer columns
            headers += [f"Column{i}" for i in range(len(headers), df.shape[1])]  # Add generic headers if needed

        # Assign headers to the DataFrame
        df.columns = headers

        # Clear and write the updated DataFrame to Excel
        df.to_excel(excel_file, index=False, engine='openpyxl')

        print(f"Successfully converted {txt_file} to {excel_file}, clearing old data and writing new data.")
    except Exception as e:
        print(f"An error occurred: {e}")

# This function is to process all the data extracted on Apollo.io ( Data Preprocessing )
def process_leads_file(input_file, output_file):
    """
    Process the leads file by combining split rows into single lines
    and write the result to a new file. Skips processing if input file doesn't exist.
    """
    # First check if input file exists
    if not os.path.exists(input_file):
        print(f"Warning: Input file '{input_file}' does not exist. Skipping processing.")
        return False
        
    def clean_and_extract_columns(input_file, output_file):
        try:
            # Clean email (4th column) if any pattern like +1
            def clean_email(email_text):
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', email_text)
                return email_match.group(1) if email_match else email_text.strip()
            
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            processed_entries = []
            for line in lines:
                # Split the line into columns
                columns = line.strip().split(',')
                
                # Extract and clean required columns
                if len(columns) >= 9:  # Ensure we have enough columns
                    name = columns[0].strip()
                    role = columns[1].strip()
                    company = columns[2].strip()
                    email = clean_email(columns[3].strip())
                    phone = columns[4].strip()
                    # columns[5] is empty
                    # columns[6] is empty
                    status = columns[7].strip()
                    location = columns[8].strip()
                    
                    # Combine the extracted columns
                    new_entry = f"{name},{role},{company},{email},{phone},{status},{location}"
                    processed_entries.append(new_entry)
            
            # Write to output file
            with open(output_file, 'w') as f:
                # Write entries
                for entry in processed_entries:
                    f.write(f"{entry}\n")
            return True
            
        except Exception as e:
            print(f"Error in clean_and_extract_columns: {str(e)}")
            return False
    
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Split the content into rough entries (split on double newlines)
        rough_entries = content.strip().split('\n\n')
        
        processed_entries = []
        current_entry = []
        
        for entry in rough_entries:
            lines = entry.strip().split('\n')
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # If line starts with a typical lead entry pattern 
                # (Name followed by role and company)
                if re.match(r'^[A-Za-z\s]+,\s*(Engineer|[A-Za-z\s]+),', line):
                    # If we have a previous entry, save it
                    if current_entry:
                        processed_entries.append(' '.join(current_entry))
                    current_entry = [line]
                else:
                    # This is a continuation line
                    if current_entry:
                        # Remove any leading commas if they exist
                        line = line.lstrip(',').strip()
                        current_entry.append(line)
        
        # Add the last entry if it exists
        if current_entry:
            processed_entries.append(' '.join(current_entry))
        
        # Write to output file
        with open(output_file, 'w') as f:
            for entry in processed_entries:
                # Clean up any multiple spaces and extra commas
                cleaned_entry = re.sub(r'\s+', ' ', entry)
                cleaned_entry = re.sub(r',\s*,', ',', cleaned_entry)
                f.write(cleaned_entry + '\n')
        
        # Process the cleaned file further
        return clean_and_extract_columns(output_file, output_file)
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False
    
# This function is to extract all the possible company names 
def check_detail_company_name(file_path):
    def initialize_driver():
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--start-maximized")
        driver = uc.Chrome(options=options)
        return driver

    def search_and_extract(driver, url, search_value, result_selector):
        try:
            driver.get(url)  # Navigate to the URL
            search_input = driver.find_element(By.ID, "search_val")  # Locate search input field
            search_input.clear()  # Clear any previous value
            search_input.send_keys(search_value)  # Enter the search value
            search_input.send_keys(Keys.RETURN)  # Hit Enter to submit the search
            time.sleep(3)  # Wait for results to load

            # Extract results
            results = driver.find_elements(By.CSS_SELECTOR, result_selector)
            return [result.text.strip() for result in results]
        except Exception as e:
            print(f"Error in search_and_extract: {str(e)}")
            return []

    try:
        driver = initialize_driver()

        with open(file_path, "r") as f:
            rows = f.readlines()
            processed_rows = []

            for row in rows:
                row = row.strip()  # Remove leading/trailing whitespace
                if not row:
                    continue  # Skip empty rows

                columns = row.split(',')
                
                # Check if this row has already been processed ( Skipping process )
                if len(columns) > 7 and columns[7].strip() and not columns[7].strip().startswith("-"):
                    processed_rows.append(row)
                    continue

                # Use the company name (third column) for search
                search_value = columns[2].strip()
                results = []

                # Check the location (last column) to determine search strategy
                if columns[-1].strip() == 'Singapore':
                    print(f"Performing search on https://www.sgpbusiness.com/ for: {search_value}")
                    results = search_and_extract(driver, "https://www.sgpbusiness.com/", search_value, "h6.list-group-item-heading.mb-0")

                    if not results:
                        print(f"No results on https://www.sgpbusiness.com/, switching to https://www.mysbusiness.com/")
                        results = search_and_extract(driver, "https://www.mysbusiness.com/", search_value, "h4.list-group-item-heading")
                else:
                    print(f"Performing search on https://www.mysbusiness.com/ for: {search_value}")
                    results = search_and_extract(driver, "https://www.mysbusiness.com/", search_value, "h4.list-group-item-heading")

                    if not results:
                        print(f"No results on https://www.mysbusiness.com/, switching to https://www.sgpbusiness.com/")
                        results = search_and_extract(driver, "https://www.sgpbusiness.com/", search_value, "h6.list-group-item-heading.mb-0")

                # Join multiple results with a hyphen, or set "No result" if no results found
                concatenated_results = "-".join(results) if results else "No result"

                # Add the results as a new column
                new_row = row + "," + concatenated_results
                processed_rows.append(new_row)

                # Print progress
                print(f"Processed {search_value}: {concatenated_results}")
                time.sleep(1)  # Small delay between searches

        # Write all processed rows back to the file
        with open(file_path, "w") as out_file:
            out_file.write("\n".join(processed_rows) + "\n")

        print("\nProcessing completed. Results have been saved to the file.")

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        try:
            driver.quit()  # Ensure the browser is closed at the end
        except:
            pass

def vtiger_login(driver , vtiger_email , vtiger_pass,each_row_email,row_data_processed):
    # Save the current window handle (original tab)
    original_tab = driver.current_window_handle
    email_processed = False # Initialize the flag 

    driver.execute_script("window.open('https://crmaccess.vtiger.com/log-in/', '_blank');")
    time.sleep(2)  # Give some time for the tab to open
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
    print("\nVTiger Logging in...")
    # If you want to debug the email, use the line below it 
    #print("Row by each row: " + each_row_email)
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    email_field.send_keys(vtiger_email)
    password_field.send_keys(vtiger_pass)
    password_field.send_keys(Keys.RETURN)
    try:
        signout_xpath = "//a[contains(@class, 'btn btn-secondary') and contains(text(), 'Sign out of all active sessions')]"

        # Wait for the element to be present
        signout_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, signout_xpath))
        )
        signout_element.click()
        print("Clicked 'Sign out of all active sessions'")
    except TimeoutException:
        # Element not found
        print("'Sign out of all active sessions' button not found. Skipping...")

    # Click for search icon to appear 
    search_icon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@title='Global Search']"))
    )
    search_icon.click()
    search_input = driver.find_element(By.XPATH, "//*[@id='global_search']")
    # got comment ken.tee@winstargroup.com.my  (checked )
    # got everything including namecard , building and person - digista@digistar.com (checked )
    # single person only - biz@carmin.com (checked )
    # none for everthing - mohd.anas@emerson.com ( checked )
    # comment only - dad
    search_input.send_keys(each_row_email)
    search_input.send_keys(Keys.RETURN)
    time.sleep(3)
    # Checkbox XPATH
    checkbox_xpath = "/html/body/div[1]/div/div[3]/div[1]/div/div/div[1]/div/div/header/div/div[3]/label/span[1]"
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkbox_xpath))
    )
    time.sleep(2)
    checkbox.click()
    
    try:
        # Check the not found XPATH div ( This XPATH is for the not found XPATH div )
        target_xpath = "//*[@id='Global_Search_Display_Modal___BV_modal_body_']/div[2]"

        # Wait until the element is visible
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, target_xpath))
        )
    except TimeoutException:
        print("element not found")
        try:
            # Locate the table container
            table_xpath = "//div[@class='allResult scrollbar scrollbar-default']"
            table_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, table_xpath))
            )

            # Locate all rows within the table
            rows = table_div.find_elements(By.XPATH, "./div")  # Adjust the XPath to match rows

            # Initialize flags to track the presence of different icons
            has_person_icon = False
            has_namecard_icon = False
            has_building_icon = False
            has_comment_icon = False

            # Check each row and update flags
            for row in rows:
                if row.find_elements(By.XPATH, ".//i[contains(@class, 'fa-contacts')]"):
                    has_person_icon = True
                if row.find_elements(By.XPATH, ".//i[contains(@class, 'fa-leads')]"):
                    has_namecard_icon = True
                if row.find_elements(By.XPATH, ".//i[contains(@class, 'fa-accounts')]"):
                    has_building_icon = True
                if row.find_elements(By.XPATH, ".//i[contains(@class, 'fa-comment')]"):
                    has_comment_icon = True

            # Evaluate the overall condition based on flags
            if (has_person_icon or has_namecard_icon or has_building_icon) and not has_comment_icon:
                print("Overall Result: Not accepted row (contains icons for person, namecard, or building but no comments)")
                row_counter = 0  # Initialize a counter outside the processing loop
                # Process each row one at a time
                with open("rejected_leads_with_email.txt", "a") as f:
                    # Increment the row counter
                    row_counter += 1

                    # Split the row into columns
                    columns = row_data_processed.split(',')

                    # Apply cleaning logic for rows except row 5
                    if row_counter != 5:
                        # Check if the last column contains a '+' and a number
                        if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                            columns[-1] = ""  # Remove the '+number' from the last column

                    # Rejoin the columns and write to the file
                    cleaned_row = ','.join(columns)
                    f.write(f"{cleaned_row}\n")

            elif has_building_icon and not (has_comment_icon or has_person_icon or has_namecard_icon):
                print("Overall Result: Accepted row (contains comments only)")
                row_counter = 0  # Initialize a counter outside the processing loop
                email_processed = True
                # Process each row one at a time
                with open("leads.txt", "a") as f:
                    # Increment the row counter
                    row_counter += 1

                    # Split the row into columns
                    columns = row_data_processed.split(',')

                    # Apply cleaning logic for rows except row 5
                    if row_counter != 5:
                        # Check if the last column contains a '+' and a number
                        if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                            columns[-1] = ""  # Remove the '+number' from the last column

                    # Rejoin the columns and write to the file
                    cleaned_row = ','.join(columns)

                    f.write(f"{cleaned_row}\n")

            elif has_comment_icon and not (has_person_icon or has_namecard_icon or has_building_icon):
                print("Overall Result: Accepted row (contains comments only)")
                row_counter = 0  # Initialize a counter outside the processing loop
                email_processed = True
                # Process each row one at a time
                with open("leads.txt", "a") as f:
                    # Increment the row counter
                    row_counter += 1

                    # Split the row into columns
                    columns = row_data_processed.split(',')

                    # Apply cleaning logic for rows except row 5
                    if row_counter != 5:
                        # Check if the last column contains a '+' and a number
                        if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                            columns[-1] = ""  # Remove the '+number' from the last column

                    # Rejoin the columns and write to the file
                    cleaned_row = ','.join(columns)

                    f.write(f"{cleaned_row}\n")

            elif has_comment_icon and (has_person_icon or has_namecard_icon or has_building_icon):
                print("Overall Result: Not accepted row (contains both comments and other icons)")
                row_counter = 0  # Initialize a counter outside the processing loop
                # Process each row one at a time
                with open("rejected_leads_with_email.txt", "a") as f:
                    # Increment the row counter
                    row_counter += 1

                    # Split the row into columns
                    columns = row_data_processed.split(',')

                    # Apply cleaning logic for rows except row 5
                    if row_counter != 5:
                        # Check if the last column contains a '+' and a number
                        if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                            columns[-1] = ""  # Remove the '+number' from the last column

                    # Rejoin the columns and write to the file
                    cleaned_row = ','.join(columns)
                    f.write(f"{cleaned_row}\n")
            else:
                print("Overall Result: Unclear criteria")
        except TimeoutException:
            print("Table or rows not found")
    else:
        print("Accepted row : No contact found on CRM")
        row_counter = 0  # Initialize a counter outside the processing loop
        email_processed = True
        # Process each row one at a time
        with open("leads.txt", "a") as f:
            # Increment the row counter
            row_counter += 1

            # Split the row into columns
            columns = row_data_processed.split(',')

            # Apply cleaning logic for rows except row 5
            if row_counter != 5:
                # Check if the last column contains a '+' and a number
                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                    columns[-1] = ""  # Remove the '+number' from the last column

            # Rejoin the columns and write to the file
            cleaned_row = ','.join(columns)
            f.write(f"{cleaned_row}\n")
    
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'fa-times') and contains(@class, 'c-pointer')]"))
    )
    close_button.click()
    
    #Sign out part 
    signout_element = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='__BVID__12__BV_toggle_']/span/a/div[1]/span"))
    )
    time.sleep(1)
    signout_element.click()
    logout_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@title='Logout']"))
    )
    time.sleep(1)
    logout_element.click()
    time.sleep(2)
    driver.close()
    # Switch back to the original tab
    driver.switch_to.window(driver.window_handles[0])
    # Original  is  driver.switch_to.window(original_tab)
    print("Switched back to the original tab.")
    return email_processed
    

def on_submit(root):
    vtiger_email_entry = vtiger_email.get()
    vtiger_password_entry = vtiger_password.get()
    num =  num_leads.get() # Number of leads 

    if not vtiger_email_entry or not vtiger_password_entry:
        messagebox.showerror("Input error", "Please enter all fields !")
        return
    
    threading.Thread(target=login_to_apollo, args=(vtiger_email_entry,vtiger_password_entry,num)).start()
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
    window_width = 600
    window_height = 400
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
    

    # VTiger Email and Password
    ttk.Label(frm, text="VTiger account credential", font=bold_font).grid(column=0, row=3, columnspan=2, pady=(20, 10), sticky="w")
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
    ttk.Label(frm, text="Enter number of leads you want to search", font=bold_font).grid(column=0, row=8, columnspan=2, pady=(0,0), sticky="w")
    ttk.Label(frm, text="Number of lead(s):").grid(column=0,row=9, sticky="w", padx=10 ,pady=5)
    global num_leads
    num_leads = ttk.Entry(frm, width=50)
    num_leads.grid(column=1,row=9, padx=10, pady=(0,0), sticky="w")
    # Login button
    ttk.Button(frm, text="Login", command=lambda: on_submit(root_apollo)).grid(column=0, row=10, columnspan=3, pady=20)

    root_apollo.mainloop() 

if __name__ == "__main__":
    apollo_login()