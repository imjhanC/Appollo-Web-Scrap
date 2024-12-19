from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

# Initialize Selenium WebDriver
def initialize_driver():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

# Function to perform search and extract results
def search_and_extract(driver, url, search_value, result_selector):
    driver.get(url)  # Navigate to the URL
    search_input = driver.find_element(By.ID, "search_val")  # Locate search input field
    search_input.clear()  # Clear any previous value
    search_input.send_keys(search_value)  # Enter the search value
    search_input.send_keys(Keys.RETURN)  # Hit Enter to submit the search
    time.sleep(3)  # Wait for results to load

    # Extract results
    results = driver.find_elements(By.CSS_SELECTOR, result_selector)
    return [result.text.strip() for result in results]

# Process the file row by row and check the last column
def process_rows_and_navigate(file_path, driver):
    try:
        with open(file_path, "r") as f:
            rows = f.readlines()
            for row in rows:
                row = row.strip()  # Remove leading/trailing whitespace
                if not row:
                    continue  # Skip empty rows

                columns = row.split(',')
                last_column = columns[-1].strip()  # Get the last column value

                # Determine the URL and search logic based on the last column
                if last_column == 'Singapore':
                    search_value = columns[2].strip()  # Third column for Singapore
                    print(f"Performing search on https://www.sgpbusiness.com/ for: {search_value}")
                    results = search_and_extract(driver, "https://www.sgpbusiness.com/", search_value, "h6.list-group-item-heading.mb-0")
                    columns.extend(results)  # Append results to columns
                else:
                    search_value = columns[2].strip()  # Third column for non-Singapore
                    print(f"Performing search on https://www.mysbusiness.com/ for: {search_value}")
                    results = search_and_extract(driver, "https://www.mysbusiness.com/", search_value, "h4.list-group-item-heading")
                    columns.extend(results)  # Append results to columns

                # Rejoin the columns into a single row and write it to the file
                cleaned_row = ','.join(columns)
                
                # Append the processed row to the 'processed_leads.txt' file
                with open("processed_leads.txt", "a") as out_file:
                    out_file.write(f"{cleaned_row}\n")
                    
                # Optionally print the row for debugging purposes
                print(f"Processed row: {cleaned_row}")

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    file_path = "leads.txt"  # Path to the leads file
    driver = initialize_driver()
    
    try:
        process_rows_and_navigate(file_path, driver)
    finally:
        driver.quit()  # Ensure the browser is closed at the end

# Run the script
if __name__ == "__main__":
    main()
