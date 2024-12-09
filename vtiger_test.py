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
    wait = WebDriverWait(driver,10)

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    email_field.send_keys("")
    password_field.send_keys("")
    password_field.send_keys(Keys.RETURN)
    time.sleep(25)

    # Click for search icon to appear 
    search_icon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@title='Global Search']"))
    )
    search_icon.click()
    search_input = driver.find_element(By.XPATH, "//*[@id='global_search']")
    # got comment ken.tee@winstargroup.com.my
    # got everything including namecard , building and person - digista@digistar.com
    # single person only - biz@carmin.com 
    # none for everthing - mohd.anas@emerson.com
    # comment only - dad
    search_input.send_keys("")
    search_input.send_keys(Keys.RETURN)

    # Checkbox XPATH
    checkbox_xpath = "/html/body/div[1]/div/div[3]/div[1]/div/div/div[1]/div/div/header/div/div[3]/label/span[1]"
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkbox_xpath))
    )
    checkbox.click()

    try:
        # Wait for results div with a relatively short timeout
        results_div = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "allResult"))
        )
            
        # Additional check to ensure div is not empty
        if results_div:
            # Check if the div contains any child elements or has non-zero content
            child_elements = results_div.find_elements(By.XPATH, ".//*")
                
            if child_elements:
                print("Results found!")
                return 'found'
        
    except TimeoutException:
        # Results div not found within timeout
        pass
        
    # Try to find "No matches" div
    try:
        no_results_div = driver.find_element(By.XPATH, "//div[contains(@class, 'my-8') and contains(@class, 'text-center')]//div[contains(@class, 'font-18') and contains(text(), 'No exact matches found')]")
            
        if no_results_div:
            print("No results found!")
            return 'not_found'
        
    except NoSuchElementException:
        # "No matches" div not found
        pass
    time.sleep(100)
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