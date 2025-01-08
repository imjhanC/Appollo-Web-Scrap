import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random
from seleniumbase import SB 

def test():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    
    # Randomized User-Agent
    from fake_useragent import UserAgent
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    print("Initializing Chrome...")
    driver = uc.Chrome(options=options)
    
    # Open target URL
    driver.get('https://google.com/')
    vtiger_login(driver)

def vtiger_login(driver):
    # Save the current window handle (original tab)
    original_tab = driver.current_window_handle
    email_processed = False # Initialize the flag 

    driver.execute_script("window.open('https://crmaccess.vtiger.com/log-in/', '_blank');")
    time.sleep(2)  # Give some time for the tab to open
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
    print("\nVTiger Logging in...")

     # Bypass Cloudflare using SeleniumBase
    def verify_success(sb):
        sb.assert_element('img[alt="Logo Assembly"]', timeout=4)
        sb.sleep(3)

    with SB(uc=True) as sb:  # Use SeleniumBase with undetected Chrome
        sb.switch_to(driver)  # Use the existing Selenium WebDriver instance
        try:
            verify_success(sb)  # Verify successful load of the page
        except Exception:
            if sb.is_element_visible('input[value*="Verify"]'):
                sb.uc_click('input[value*="Verify"]')
            else:
                sb.uc_gui_click_captcha()  # Handle CAPTCHA if present
            try:
                verify_success(sb)
            except Exception:
                raise Exception("CAPTCHA detection failed!")

    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        # Simulate typing with delay
        for char in "example@example.com":
            email_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        for char in "password123":
            password_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Click Login button (if applicable)
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        print("Login submitted.")
    except Exception as e:
        print(f"Error during login: {e}")
    finally:

        driver.switch_to.window(driver.window_handles[0])
        driver.close()
        time.sleep(1000)

if __name__ == "__main__":
    test()
