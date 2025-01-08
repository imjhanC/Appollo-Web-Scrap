from seleniumbase import SB
import time

with SB(uc=True) as sb:
    # Open the original tab and navigate to example.com
    sb.open("https://example.com")
    
    # Open a new tab and navigate to the desired URL
    sb.open_new_tab("about:blank")  # Open a blank tab first
    time.sleep(3)
    sb.get("https://crmaccess.vtiger.com/log-in/")  # Navigate to the desired URL

    # Switch to the new tab (index 1 since tabs are zero-indexed)
    sb.switch_to_tab(0)
    
    # Perform actions on the new tab
     # Wait for the username field to appear and input the email
    sb.type('input[name="username"]', 'xxx', timeout=10)  # Waits up to 10 seconds
    
    # Wait for the password field to appear and input the password
    sb.type('input[name="password"]', 'vtiger_pass', timeout=10)  # Waits up to 10 seconds
    
    # Submit the login form (simulating the ENTER key)
    sb.click('button[type="submit"]')  # Adjust selector if necessary
    
    # Stay on the new tab for further interactions
    #sb.click("#loginButton")  # Example action: Clicking a button
    sb.switch_to_tab(1)
    heading_text = sb.get_text("/html/body/div/h1")
    
    # Print the retrieved text
    print("Heading text:", heading_text)
    
    time.sleep(1000)