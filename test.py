from selenium import webdriver

# Open the URL
driver = webdriver.Chrome()
driver.get("https://www.ssm.com.my")

# Switch to the browser authentication dialog
alert = driver.switch_to.alert

# Enter the username and password
alert.send_keys("your_username")
alert.send_keys("\t")  # Tab to move to the password field
alert.send_keys("your_password")
alert.accept()  # Click "Sign In"