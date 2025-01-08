from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
import time

def check_detail_company_name(file_path):
    def search_and_extract(sb, url, search_value, result_selector):
        try:
            sb.open(url)  # Navigate to URL using SeleniumBase
            
            # Wait for and interact with search input
            sb.wait_for_element("#search_val")
            sb.clear("#search_val")
            
            # Type the search value and send RETURN key
            search_input = sb.get_element("#search_val")
            search_input.send_keys(search_value + Keys.RETURN)
            
            # Wait for results to load
            time.sleep(3)
            
            # Extract results using SeleniumBase's find_elements
            results = sb.find_elements(result_selector)
            return [result.text.strip() for result in results]
            
        except Exception as e:
            print(f"Error in search_and_extract: {str(e)}")
            return []

    try:
        # Initialize SeleniumBase with undetected chromedriver
        with SB(uc=True) as sb:
            # Configure browser settings
            sb.maximize_window()
            
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
                    search_value = columns[2].strip()
                    results = []

                    # Check location and determine search strategy
                    if columns[-1].strip() == 'Singapore':
                        print(f"Performing search on https://www.sgpbusiness.com/ for: {search_value}")
                        results = search_and_extract(
                            sb,
                            "https://www.sgpbusiness.com/",
                            search_value,
                            "h6.list-group-item-heading.mb-0"
                        )

                        if not results:
                            print(f"No results on https://www.sgpbusiness.com/, switching to https://www.mysbusiness.com/")
                            results = search_and_extract(
                                sb,
                                "https://www.mysbusiness.com/",
                                search_value,
                                "h4.list-group-item-heading"
                            )
                    else:
                        print(f"Performing search on https://www.mysbusiness.com/ for: {search_value}")
                        results = search_and_extract(
                            sb,
                            "https://www.mysbusiness.com/",
                            search_value,
                            "h4.list-group-item-heading"
                        )

                        if not results:
                            print(f"No results on https://www.mysbusiness.com/, switching to https://www.sgpbusiness.com/")
                            results = search_and_extract(
                                sb,
                                "https://www.sgpbusiness.com/",
                                search_value,
                                "h6.list-group-item-heading.mb-0"
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

# Usage example
if __name__ == "__main__":
    check_detail_company_name("leads.txt")