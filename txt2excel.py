import pandas as pd

def txt_to_excel(txt_file, excel_file):
    try:
        # Try reading the file, handle inconsistent columns
        df = pd.read_csv(txt_file, sep=',', header=None, on_bad_lines='skip')  # Skip bad lines

        # Define headers manually (you can adjust these based on your data)
        headers = [
            'Name', 'Position', 'Company', 'Email', 'Phone', 'Field1', 'Field2',
            'City', 'Country', 'Quantity', 'Industry', 'Specialization', 'Countries',
            'Company Full Name', 'Company Name'
        ]
        
        # Assign headers to the DataFrame
        df.columns = headers
        
        # Check if the output Excel file already exists
        try:
            existing_df = pd.read_excel(excel_file, engine='openpyxl')
            # Append new data to the existing DataFrame
            df = existing_df.append(df, ignore_index=True)
        except FileNotFoundError:
            # If the file doesn't exist, it's the first time creating it
            pass
        
        # Write the DataFrame to Excel
        df.to_excel(excel_file, index=False, engine='openpyxl')

        print(f"Successfully converted {txt_file} to {excel_file} with headers")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
txt_file = "processed_leads.txt"  # Path to the text file
excel_file = "leads.xlsx"  # Desired output Excel file path

txt_to_excel(txt_file, excel_file)
