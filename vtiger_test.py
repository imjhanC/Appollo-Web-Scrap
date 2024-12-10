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

def main():
    driver = None
    options = uc.ChromeOptions()
    options.add_argument("--start-minimized")
    driver = uc.Chrome(options=options) 
    driver.get('https://crmaccess.vtiger.com/log-in/')

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    email_field.send_keys("")
    password_field.send_keys("")
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
    search_input.send_keys("ken.tee@winstargroup.com.my")
    search_input.send_keys(Keys.RETURN)
    time.sleep(3)
    # Checkbox XPATH
    checkbox_xpath = "/html/body/div[1]/div/div[3]/div[1]/div/div/div[1]/div/div/header/div/div[3]/label/span[1]"
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkbox_xpath))
    )
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
            elif has_comment_icon and not (has_person_icon or has_namecard_icon or has_building_icon):
                print("Overall Result: Accepted row (contains comments only)")
            elif has_comment_icon and (has_person_icon or has_namecard_icon or has_building_icon):
                print("Overall Result: Not accepted row (contains both comments and other icons)")
            else:
                print("Overall Result: Unclear criteria")
        except TimeoutException:
            print("Table or rows not found")
    else:
        print("element found")
    
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'fa-times') and contains(@class, 'c-pointer')]"))
    )
    close_button.click()

    #Sign out part 
    signout_element = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='__BVID__12__BV_toggle_']/span/a/div[1]/span"))
    )
    signout_element.click()
    logout_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@title='Logout']"))
    )
    logout_element.click()
    time.sleep(500)

if __name__  == "__main__":
    main()