def process_leads_files(file_paths):
    """
    Process multiple leads files and clean their data to ensure exactly 7 columns per row.
    Adds a trailing comma after the last column.
    
    Args:
        file_paths (list): List of file paths to process
    """
    def clean_data(input_text):
        # Split into lines and remove empty lines
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        cleaned_rows = []
        
        for line in lines:
            # Split the line by comma and trim whitespace
            columns = [col.strip() for col in line.split(',')]
            
            # Skip obviously invalid rows
            if len(columns) < 3:
                continue
            
            # Extract the relevant columns
            name = columns[0]
            role = columns[1]
            company = columns[2]
            email_access = columns[3]
            mobile_access = columns[4]
            # Find the city/location (it appears before Malaysia/Singapore)
            city = None
            country = None
            
            # Search for the location and country
            for i in range(len(columns)):
                if columns[i].strip() in ['Malaysia', 'Singapore']:
                    country = columns[i].strip()
                    # City is the value before the country
                    if i > 0:
                        city = columns[i-1].strip()
                    break
            
            # If no city/country found, use defaults
            if not city:
                city = ''
            if not country:
                country = 'Malaysia'
            
            # Combine the columns in the correct order
            cleaned_row = [
                name,
                role,
                company,
                email_access,
                mobile_access,
                city,
                country
            ]
            
            # Only add rows that have at least a name and role
            if cleaned_row[0] and cleaned_row[1]:
                # Add the trailing comma after joining the columns
                cleaned_rows.append(','.join(cleaned_row) + ',')
        
        return cleaned_rows

    # Process each file
    for file_path in file_paths:
        try:
            # Read input file
            with open(file_path, 'r') as file:
                input_text = file.read()

            # Clean the data
            cleaned_data = clean_data(input_text)

            # Write back to the same file
            with open(file_path, 'w') as file:
                for row in cleaned_data:
                    file.write(row + '\n')

            print(f"Successfully processed: {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

def main():
    files_to_process = [
        'leads_copy.txt',
    ]
    process_leads_files(files_to_process)

if __name__ == "__main__":
    main()