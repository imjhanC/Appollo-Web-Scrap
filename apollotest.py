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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test():
    with SB(uc=True) as sb:
        sb.open('https://crmaccess.vtiger.com/log-in/')
        sb.type('input[name="username"]', '', timeout=10)
        sb.type('input[name="password"]', '', timeout=10)
        sb.click('button[type="submit"]')
        time.sleep(5)
        sb.click('[title="Global Search"]',timeout=20)
        sb.type('#global_search', '')
        sb.find_element('#global_search').send_keys(Keys.ENTER)


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
                    
                    
                elif has_building_icon and not (has_comment_icon or has_person_icon or has_namecard_icon):
                    print("Overall Result: Accepted row (contains building icon only)")
                    email_processed = True
                    
                    
                elif has_comment_icon and not (has_person_icon or has_namecard_icon or has_building_icon):
                    print("Overall Result: Accepted row (contains comments only)")
                    email_processed = True
                   
                    
                elif has_comment_icon and (has_person_icon or has_namecard_icon or has_building_icon):
                    print("Overall Result: Not accepted row (contains both comments and other icons)")
                    
                    
                else:
                    print("Overall Result: Unclear criteria")
                    
            except Exception:
                print("Table or rows not found")
        
        # Close search results
        sb.click('.fa-times.c-pointer')
        
        # Sign out process
        sb.click('#__BVID__12__BV_toggle_ span a div span')
        sb.sleep(1)
        sb.click('[title="Logout"]')
        sb.sleep(2)
        
        time.sleep(1000)

test()