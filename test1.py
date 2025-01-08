from seleniumbase import SB

def open_new_tab_with_seleniumbase():
    with SB(uc=True) as sb:  # Use SeleniumBase with undetected Chrome
        # Open the initial page (Google, for example)
        sb.open("https://google.com/")
        print("Initial page loaded.")
        
        # Get the current window handle (Google tab)
        google_tab = sb.driver.current_window_handle
        
        # Open a new tab
        sb.open_new_window()
        print("New tab opened.")

        # Navigate to VTiger in the new tab
        sb.open("https://crmaccess.vtiger.com/log-in/")
        print("Navigated to VTiger in the new tab.")
        
        # Perform any actions in the new tab (VTiger)
        sb.assert_text("Login", "body", timeout=10)
        print("Login page verified in VTiger.")

        # Switch back to the Google tab
        sb.switch_to_window(google_tab)
        print("Switched back to the Google tab.")

        # You can continue interacting with the Google page here if needed
        sb.assert_text("Google", "title")
        print("Google tab verified again.")

# Run the function
open_new_tab_with_seleniumbase()
