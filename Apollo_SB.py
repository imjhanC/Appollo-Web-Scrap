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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

# Login part GUI  
def on_submit(root):
    vtiger_email_entry = vtiger_email.get()
    vtiger_password_entry = vtiger_password.get()
    num =  num_leads.get() # Number of leads 

    if not vtiger_email_entry or not vtiger_password_entry:
        messagebox.showerror("Input error", "Please enter all fields !")
        return
    
    threading.Thread(target=login_to_apollo, args=(vtiger_email_entry,vtiger_password_entry,num)).start()
    root.destroy()

def login_window():
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

# This is the logiv for interacting inside the apollo.io
def login_to_apollo(vtiger_email, vtiger_pass, num_leads):

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
    
    print("Logging in...")
    # Process starts here
    with SB(uc=True) as sb:
        try:
            sb.open('https://app.apollo.io/#/login')
            countdown = TwoFactorCountdown()
            threading.Thread(target=countdown.start, daemon=True).start()
            # Wait until the "Continue" button is clicked
            countdown.continue_event.wait()
            sb.wait_for_element('//span[@class="zp_tZMYK" and text()="Hide Filters"]', timeout=10)  # Wait for 10 seconds
            sb.click('//span[@class="zp_tZMYK" and text()="Hide Filters"]')  # Click the element

            tracking_file = "tracking.txt"
            emails = extract_emails_from_file(tracking_file)
            emails_json = json.dumps(emails, indent=4)
            print("Extracted Emails in JSON Format:")
            print(emails_json)

            # Initialize the lead processing
            target_leads = int(num_leads)
            successful_leads = 0
            page_num = 1
            all_leads = 0

            while successful_leads < target_leads:
                try:
                    # Wait for the target div containing rows
                    # FIXED: Added proper wait strategy matching Selenium's explicit wait
                    sb.wait_for_element(".zp_tFLCQ", timeout=10)
                    
                    # FIXED: Get the container first, then find rows within it
                    container = sb.find_element(".zp_tFLCQ")
                    rows = container.find_elements('xpath', './div')  # Use relative xpath

                    print(f"Processing rows on Page {page_num}:")
                    for i, row in enumerate(rows):
                        if successful_leads >= target_leads:
                            break

                        # Locate all columns within the current row
                        columns = row.find_elements('xpath', './*')
                        
                        row_data = [column.text for column in columns]
                        row_data_processed = ", ".join(row_data)
                        print(f"Processing row: {', '.join(row_data)}")
                        
                        if len(columns) < 4:
                            print("Skipping: Insufficient columns")
                            continue
                        
                        fourth_column = columns[3].text.strip()
                        fourth_column_text = re.sub(r'\+\d+', '', fourth_column).strip()
                        
                        if fourth_column_text in emails_json:
                            print(f"Skipping: Already processed - {fourth_column_text}")
                            all_leads += 1
                            # FIXED: Moved row_counter initialization outside the with block
                            row_counter = 0
                            with open("skipped_email.txt", "a") as f:
                                row_counter += 1
                                columns = row_data_processed.split(',')
                                if row_counter != 5:
                                    if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                        columns[-1] = ""
                                cleaned_row = ','.join(columns)
                                f.write(f"{cleaned_row}\n")
                            continue

                        email_processed = False

                        # Handle "Access email" case
                        if fourth_column_text == "Access email":
                            # FIXED: Made XPath more specific to match Selenium implementation
                            access_email_buttons = row.find_elements(
                                'xpath',
                                ".//div[4]/div/span/button/span"  # Using relative path
                            )
                            if access_email_buttons:
                                access_email_buttons[0].click()
                                sb.sleep(5)  # Using SeleniumBase's sleep method
                                
                                # Re-fetch columns after click
                                columns = row.find_elements('xpath', './*')
                                if len(columns) >= 4:
                                    fourth_column = columns[3].text.strip()
                                    fourth_column_text = re.sub(r'\+\d+', '', fourth_column).strip()
                                    email_address = fourth_column_text.split('+')[0].strip()

                                    if '@' in email_address and '.' in email_address:
                                        # Update row_data with new email
                                        row_data = [column.text for column in columns]
                                        row_data[3] = email_address
                                        row_data_processed = ", ".join(row_data)

                                        with open("tracking.txt", "a") as f:
                                            f.write(f"{email_address}\n")
                                        
                                        print(f"Success: Access email updated - {email_address}")
                                        email_processed = vtiger_login(sb, vtiger_email, vtiger_pass, email_address, row_data_processed)
                                        all_leads += 1
                                    else:
                                        all_leads += 1
                                        # FIXED: Properly handle rejected leads
                                        with open("rejected_leads.txt", "a") as f:
                                            columns = row_data_processed.split(',')
                                            if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                                columns[-1] = ""
                                            cleaned_row = ','.join(columns)
                                            f.write(f"{cleaned_row}\n")
                                        continue

                        elif fourth_column_text == "Save contact":
                            all_leads += 1
                            print(f"Skipping: Save contact button")
                            with open("rejected_leads.txt", "a") as f:
                                columns = row_data_processed.split(',')
                                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                    columns[-1] = ""
                                cleaned_row = ','.join(columns)
                                f.write(f"{cleaned_row}\n")
                            continue

                        elif fourth_column_text == "No email":
                            all_leads += 1
                            print(f"Skipping: No email button")
                            with open("rejected_leads.txt", "a") as f:
                                columns = row_data_processed.split(',')
                                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                                    columns[-1] = ""
                                cleaned_row = ','.join(columns)
                                f.write(f"{cleaned_row}\n")
                            continue
                        
                        elif "@" in fourth_column_text:
                            email_address = fourth_column_text.split('+')[0].strip()
                            with open("tracking.txt", "a") as f:
                                f.write(f"{email_address}\n")
                            
                            print(f"Success: Direct email - {email_address}")
                            email_processed = vtiger_login(sb, vtiger_email, vtiger_pass, email_address, row_data_processed)
                            all_leads += 1
                        
                        if email_processed:
                            successful_leads += 1
                            print(f"Progress: {successful_leads}/{target_leads} Successful leads processed")

                    if successful_leads < target_leads:
                        try:
                            # FIXED: Updated next page button selector to match Selenium implementation
                            next_page_button = sb.find_element("css: i.apollo-icon-chevron-arrow-right")
                            next_page_button.click()
                            sb.sleep(3)
                            page_num += 1
                        except Exception:
                            print("Reached the last page. Cannot find more leads.")
                            break

                except Exception as e:
                    print(f"Error processing page {page_num}: {e}")
                    break

            if successful_leads < target_leads:
                print(f"Warning: Could only process {successful_leads} leads out of {target_leads} requested.")
        except Exception as e:
            print(f"Error in login to Apollo part 1: {str(e)}")
        finally:
            sb.driver.quit()

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
    

def vtiger_login(sb, vtiger_email, vtiger_pass, each_row_email, row_data_processed):
    def save_to_file(filename, row_data):
        row_counter = 0
        with open(filename, "a") as f:
            row_counter += 1
            columns = row_data.split(',')
            
            # Clean phone numbers except for row 5
            if row_counter != 5:
                if len(columns) > 0 and columns[-1].strip().startswith('+') and columns[-1].strip()[1:].isdigit():
                    columns[-1] = ""
            
            cleaned_row = ','.join(columns)
            f.write(f"{cleaned_row}\n")

    # Flag to determine whether the email has been processed 
    email_processed = False
    
    # Open new tab with VTiger login
    sb.open_new_tab("about:blank")
    time.sleep(1)
    sb.get('https://crmaccess.vtiger.com/log-in/')
    sb.switch_to_tab(0)
    print("\nVTiger Logging in...")

    # Handle Cloudflare verification
    #try:
    #    sb.assert_element('img[alt="Logo Assembly"]', timeout=4)
    #    sb.sleep(3)
    #except Exception:
    #    if sb.is_element_visible('input[value*="Verify"]'):
    #        sb.uc_click('input[value*="Verify"]')
    #    else:
    #        sb.uc_gui_click_captcha()
    #    try:
    #        sb.assert_element('img[alt="Logo Assembly"]', timeout=4)
    #        sb.sleep(3)
    #    except Exception:
    #        raise Exception("CAPTCHA detection failed!")

    # Login process
    sb.type('input[name="username"]', vtiger_email, timeout=10)
    sb.type('input[name="password"]', vtiger_pass, timeout=10)
    sb.click('button[type="submit"]')

    # Handle active sessions if present
    try:
        sb.click('a.btn.btn-secondary:contains("Sign out of all active sessions")', timeout=5)
        print("Clicked 'Sign out of all active sessions'")
    except Exception:
        print("'Sign out of all active sessions' button not found. Skipping...")

    # Global search
    time.sleep(5)
    # Ensure login is complete by waiting for the user menu or dashboard
    sb.wait_for_element('[title="Global Search"]', timeout=15)  # Adjust selector based on VTiger's UI
    sb.click('[title="Global Search"]',timeout=20)
    sb.type('#global_search', each_row_email)
    sb.find_element('#global_search').send_keys(Keys.ENTER)
    sb.sleep(3)
    
    # Click checkbox
    # Access the underlying WebDriver to use Selenium
    driver = sb.driver  # Get the WebDriver instance from SeleniumBase

    # Perform Selenium-specific actions (clicking using Selenium)
    try:
        # Example of clicking using Selenium
        checkbox = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/div[1]/div/div/div[1]/div/div/header/div/div[3]/label/span[1]'))
        )
        checkbox.click()  # Click the checkbox
        print("Clicked on checkbox using Selenium")
    except Exception as e:
        print(f"Error while clicking: {e}")

        # Return to SeleniumBase for further actions
        sb.sleep(2)  # Give a brief pause before switching back to SeleniumBase


    try:
        # Check for "not found" message
        not_found_selector = '#Global_Search_Display_Modal___BV_modal_body_ > div:nth-child(2)'
        sb.wait_for_element(not_found_selector, timeout=10)
        print("Accepted row : No contact found on CRM")
        email_processed = True
        save_to_file("leads.txt", row_data_processed)
        
    except Exception:
        try:
            # Check search results
            table_selector = '.allResult.scrollbar.scrollbar-default'
            sb.wait_for_element(table_selector)
            
            # Initialize icon flags
            has_person_icon = sb.is_element_present('.fa-contacts')
            has_namecard_icon = sb.is_element_present('.fa-leads')
            has_building_icon = sb.is_element_present('.fa-accounts')
            has_comment_icon = sb.is_element_present('.fa-comment')
            
            # Process results based on icons present
            if (has_person_icon or has_namecard_icon or has_building_icon) and not has_comment_icon:
                print("Overall Result: Not accepted row (contains icons for person, namecard, or building but no comments)")
                save_to_file("rejected_leads_with_email.txt", row_data_processed)
                
            elif has_building_icon and not (has_comment_icon or has_person_icon or has_namecard_icon):
                print("Overall Result: Accepted row (contains building icon only)")
                email_processed = True
                save_to_file("leads.txt", row_data_processed)
                
            elif has_comment_icon and not (has_person_icon or has_namecard_icon or has_building_icon):
                print("Overall Result: Accepted row (contains comments only)")
                email_processed = True
                save_to_file("leads.txt", row_data_processed)
                
            elif has_comment_icon and (has_person_icon or has_namecard_icon or has_building_icon):
                print("Overall Result: Not accepted row (contains both comments and other icons)")
                save_to_file("rejected_leads_with_email.txt", row_data_processed)
                
            else:
                print("Overall Result: Unclear criteria")
                
        except Exception:
            print("Table or rows not found")
    
    # Close search results
    sb.click('.fa-times.c-pointer')

    #To prevent switching to original tab without logging out and closing VTiger tab
    try:
        # Sign out process
        sb.click('#__BVID__12__BV_toggle_ span a div span')
        sb.sleep(1)
        sb.click('[title="Logout"]')
        sb.sleep(2)
    
        # Close current window and switch back to original
        sb.driver.close()

        #sb.switch_to_tab(1)
        sb.switch_to_default_window()
        print("Switched back to the original tab.")
    except Exception as e:
        print(f"Error during logout process: {e}")

    return email_processed

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
    def search_and_extract(sb, search_value, result_selector):
        try:
            search_input_css = "#search_val"
            sb.wait_for_element_present(search_input_css, timeout=10)

            # Wait for the input field to be visible, enabled, and interactable
            WebDriverWait(sb.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_input_css))
            )

            search_input = sb.get_element(search_input_css)
            search_input.clear()  # Clear the field if needed
            sb.click("body")
            time.sleep(0.5)

            search_input.click()
            time.sleep(0.5)
            # Type the search value and send RETURN key
            search_input.send_keys(search_value + Keys.RETURN)

            # Wait for results to load
            WebDriverWait(sb.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, result_selector))
            )
            
            # Wait for results to load
            time.sleep(3)
            
            # Extract results using SeleniumBase's find_elements
            results = sb.find_elements(result_selector)
            return [result.text.strip() for result in results]
            
        except Exception as e:
            print(f"Error in search_and_extract at with search value '{search_value}': {str(e)}")
            return []

    try:
        sg_selector = "h6.list-group-item-heading.mb-0"
        my_selector = "h4.list-group-item-heading"
        # Initialize SeleniumBase with undetected chromedriver
        with SB(uc=True) as sb:
            # Configure browser settings
            sb.maximize_window()

            #Preload sites to render elements
            sb.open("https://www.mysbusiness.com/")
            sb.open("https://www.sgpbusiness.com/")
            
            with open(file_path, "r") as f:
                rows = f.readlines()
                processed_rows = []

                for row in rows:
                    row = row.strip()
                    if not row:
                        continue

                    columns = row.split(',')
                    
                    # Skip already processed rows
                    if len(columns) > 7 and columns[7].strip() and not columns[7].strip().startswith("-"):
                        processed_rows.append(row)
                        continue

                    # Get company name for search
                    search_value = ''
                    search_value = columns[2].strip()
                    results = []

                    # Check location and determine search strategy
                    if columns[-1].strip() == 'Singapore':
                        print(f"Performing search on SG for: {search_value}")
                        sb.open("https://www.sgpbusiness.com/")
                        results = search_and_extract(
                            sb,
                            search_value,
                            sg_selector
                        )

                    else:
                        print(f"Performing search on MY for: {search_value}")
                        sb.open("https://www.mysbusiness.com/")
                        results = search_and_extract(
                            sb,
                            search_value,
                            my_selector
                        )

                    # Process results
                    concatenated_results = "-".join(results) if results else "No result"
                    new_row = row + "," + concatenated_results
                    processed_rows.append(new_row)

                    # Print progress
                    print(f"Processed {search_value}: {concatenated_results}")
                    time.sleep(1)  # Small delay between searches

            # Write processed rows back to file
            with open(file_path, "w") as out_file:
                out_file.write("\n".join(processed_rows) + "\n")

            print("\nProcessing completed. Results have been saved to the file.")

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    login_window()