from tkinter import * 
from tkinter import ttk, messagebox # Correctly import ttk for themed widgets
from PIL import Image, ImageTk

# Declare global variables at the top of your script
job_titles_value = []
location_value = []
industry_value = []

previous_text1 = ""
previous_text2 = ""
previous_text3 = ""

def reload_dropdowns():
    """Reload all dropdown values from their respective files"""
    global job_titles_dropdown, location_dropdown, industries_dropdown
    
    # Read updated values from files
    job_titles = read_file("jobtitle.txt")
    locations = read_file("location.txt")
    industries = read_file("industry.txt")
    
    # Update dropdown values
    job_titles_dropdown['values'] = job_titles
    location_dropdown['values'] = locations
    industries_dropdown['values'] = industries
    
    # Clear current selections
    job_titles_dropdown.set('')
    location_dropdown.set('')
    industries_dropdown.set('')
    
def setting():
    # Function to handle the opening of the industry section
    def on_industry_click():
        # Remove any existing widgets before creating a new one
        for widget in text_frame.winfo_children():
            widget.destroy()

        # Create a label for "Industry"
        label_industry = ttk.Label(text_frame, text="Edit / Add Industry:", font=("Helvetica", 10, "bold"))
        label_industry.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Create a Text widget for displaying/editing industry content
        text_industry = Text(text_frame, width=50, height=15, wrap="word")
        text_industry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Add a scrollbar for the Text widget
        scrollbar_industry = ttk.Scrollbar(text_frame, orient="vertical", command=text_industry.yview)
        scrollbar_industry.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
        text_industry.config(yscrollcommand=scrollbar_industry.set)

        # Add an Entry widget to add a new industry
        entry_industry = ttk.Entry(text_frame, width=62)
        entry_industry.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Placeholder text for entry_industry
        placeholder_industry = "Enter new industry here..."

        def on_focus_in_industry(event):
            if entry_industry.get() == placeholder_industry:
                entry_industry.delete(0, END)  # Clear placeholder text
                entry_industry.config(foreground="black")

        def on_focus_out_industry(event):
            if entry_industry.get() == "":
                entry_industry.insert(0, placeholder_industry)
                entry_industry.config(foreground="gray")

        # Set the placeholder text initially
        entry_industry.insert(0, placeholder_industry)
        entry_industry.config(foreground="gray")

        # Bind focus events to handle placeholder text
        entry_industry.bind("<FocusIn>", on_focus_in_industry)
        entry_industry.bind("<FocusOut>", on_focus_out_industry)

        # Save button for the new industry
        def save_new_industry():
            new_industry = entry_industry.get()
            if new_industry and new_industry != placeholder_industry:
                # Append to the industry.txt file
                with open("industry.txt", "a") as file:
                    file.write(new_industry + "\n")
                # Clear the entry widget and reload content
                entry_industry.delete(0, END)
                load_industry()  # Reload the industry content to reflect the new addition

        # Save button for the content of Text widget (Industry)
        def save_industry():
            content = text_industry.get("1.0", "end-1c")  # Get the content from the Text widget
            with open("industry.txt", "w") as file:
                file.write(content)  # Write the content to the file
            load_industry()  # Reload content after saving

        # Clear button for the entry field
        def clear_industry_entry():
            entry_industry.delete(0, END)

        def save_combined():
            save_new_industry()
            save_industry()

        save_button = ttk.Button(text_frame, text="Save", command=save_combined)
        save_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        clear_button = ttk.Button(text_frame, text="Clear", command=clear_industry_entry)
        clear_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Refresh button to reload the content
        def load_industry():
            try:
                with open("industry.txt", "r") as file:
                    content = file.read()
                    text_industry.delete("1.0", "end")  # Clear any existing content
                    text_industry.insert("1.0", content)
            except FileNotFoundError:
                text_industry.delete("1.0", "end")
                text_industry.insert("1.0", "industry.txt file not found.")

        load_industry()  # Load content initially


    # Function to handle the opening of the job title section
    def on_jobtitle_click():
        # Remove any existing widgets before creating a new one
        for widget in text_frame.winfo_children():
            widget.destroy()

        # Create a label for "Job Title"
        label_jobtitle = ttk.Label(text_frame, text="Edit / Add Job Title:", font=("Helvetica", 10, "bold"))
        label_jobtitle.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Create a Text widget for displaying/editing job title content
        text_jobtitle = Text(text_frame, width=50, height=15, wrap="word")
        text_jobtitle.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Add a scrollbar for the Text widget
        scrollbar_jobtitle = ttk.Scrollbar(text_frame, orient="vertical", command=text_jobtitle.yview)
        scrollbar_jobtitle.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
        text_jobtitle.config(yscrollcommand=scrollbar_jobtitle.set)

        # Add an Entry widget to add a new job title
        entry_jobtitle = ttk.Entry(text_frame, width=62)
        entry_jobtitle.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Placeholder text for entry_jobtitle
        placeholder_jobtitle = "Enter new job title here..."

        def on_focus_in_jobtitle(event):
            if entry_jobtitle.get() == placeholder_jobtitle:
                entry_jobtitle.delete(0, END)  # Clear placeholder text
                entry_jobtitle.config(foreground="black")

        def on_focus_out_jobtitle(event):
            if entry_jobtitle.get() == "":
                entry_jobtitle.insert(0, placeholder_jobtitle)
                entry_jobtitle.config(foreground="gray")

        # Set the placeholder text initially
        entry_jobtitle.insert(0, placeholder_jobtitle)
        entry_jobtitle.config(foreground="gray")

        # Bind focus events to handle placeholder text
        entry_jobtitle.bind("<FocusIn>", on_focus_in_jobtitle)
        entry_jobtitle.bind("<FocusOut>", on_focus_out_jobtitle)

        # Save button for the new job title
        def save_new_jobtitle():
            new_jobtitle = entry_jobtitle.get()
            if new_jobtitle and new_jobtitle != placeholder_jobtitle:
                # Append to the jobtitle.txt file
                with open("jobtitle.txt", "a") as file:
                    file.write(new_jobtitle + "\n")
                # Clear the entry widget and reload content
                entry_jobtitle.delete(0, END)
                load_jobtitle()  # Reload the job title content to reflect the new addition

        # Save button for the content of Text widget (Job Title)
        def save_jobtitle():
            content = text_jobtitle.get("1.0", "end-1c")  # Get the content from the Text widget
            with open("jobtitle.txt", "w") as file:
                file.write(content)  # Write the content to the file
            load_jobtitle()  # Reload content after saving

        # Clear button for the entry field
        def clear_jobtitle_entry():
            entry_jobtitle.delete(0, END)

        def save_combined():
            save_new_jobtitle()
            save_jobtitle()

        save_button = ttk.Button(text_frame, text="Save", command=save_combined)
        save_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        clear_button = ttk.Button(text_frame, text="Clear", command=clear_jobtitle_entry)
        clear_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Refresh button to reload the content
        def load_jobtitle():
            try:
                with open("jobtitle.txt", "r") as file:
                    content = file.read()
                    text_jobtitle.delete("1.0", "end")  # Clear any existing content
                    text_jobtitle.insert("1.0", content)
            except FileNotFoundError:
                text_jobtitle.delete("1.0", "end")
                text_jobtitle.insert("1.0", "jobtitle.txt file not found.")

        load_jobtitle()  # Load content initially


    # Function to handle the opening of the location section
    def on_location_click():
        # Remove any existing widgets before creating a new one
        for widget in text_frame.winfo_children():
            widget.destroy()

        # Create a label for "Location"
        label_location = ttk.Label(text_frame, text="Edit / Add Location:", font=("Helvetica", 10, "bold"))
        label_location.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Create a Text widget for displaying/editing location content
        text_location = Text(text_frame, width=50, height=15, wrap="word")
        text_location.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Add a scrollbar for the Text widget
        scrollbar_location = ttk.Scrollbar(text_frame, orient="vertical", command=text_location.yview)
        scrollbar_location.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
        text_location.config(yscrollcommand=scrollbar_location.set)

        # Add an Entry widget to add a new location
        entry_location = ttk.Entry(text_frame, width=62)
        entry_location.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Placeholder text for entry_location
        placeholder_location = "Enter new location here..."

        def on_focus_in_location(event):
            if entry_location.get() == placeholder_location:
                entry_location.delete(0, END)  # Clear placeholder text
                entry_location.config(foreground="black")

        def on_focus_out_location(event):
            if entry_location.get() == "":
                entry_location.insert(0, placeholder_location)
                entry_location.config(foreground="gray")

        # Set the placeholder text initially
        entry_location.insert(0, placeholder_location)
        entry_location.config(foreground="gray")

        # Bind focus events to handle placeholder text
        entry_location.bind("<FocusIn>", on_focus_in_location)
        entry_location.bind("<FocusOut>", on_focus_out_location)

        # Save button for the new location
        def save_new_location():
            new_location = entry_location.get()
            if new_location and new_location != placeholder_location:
                # Append to the location.txt file
                with open("location.txt", "a") as file:
                    file.write(new_location + "\n")
                # Clear the entry widget and reload content
                entry_location.delete(0, END)
                load_location()  # Reload the location content to reflect the new addition

        # Save button for the content of Text widget (Location)
        def save_location():
            content = text_location.get("1.0", "end-1c")  # Get the content from the Text widget
            with open("location.txt", "w") as file:
                file.write(content)  # Write the content to the file
            load_location()  # Reload content after saving

        # Clear button for the entry field
        def clear_location_entry():
            entry_location.delete(0, END)

        def save_combined():
            save_new_location()
            save_location()

        save_button = ttk.Button(text_frame, text="Save", command=save_combined)
        save_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        clear_button = ttk.Button(text_frame, text="Clear", command=clear_location_entry)
        clear_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Refresh button to reload the content
        def load_location():
            try:
                with open("location.txt", "r") as file:
                    content = file.read()
                    text_location.delete("1.0", "end")  # Clear any existing content
                    text_location.insert("1.0", content)
            except FileNotFoundError:
                text_location.delete("1.0", "end")
                text_location.insert("1.0", "location.txt file not found.")

        load_location()  # Load content initially




    root_setting = Toplevel(root)  # Create a new top-level window
    root_setting.title("Settings") 
    window_width = 1270
    window_height = 600
    screen_width = root_setting.winfo_screenwidth()  # Get screen width
    screen_height = root_setting.winfo_screenheight()  # Get screen height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root_setting.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root_setting.resizable(False, False)
    root_setting.columnconfigure(0, weight=1)
    root_setting.rowconfigure(0, weight=1)
    root_setting.transient(root)  # Keep the window on top
    root_setting.grab_set()  # Prevent interaction with the parent window

    setting_frm = ttk.Frame(root_setting, padding=20)
    setting_frm.grid(row=0, column=0, sticky="nsew")

    # Create a separate frame for the Text widget
    text_frame = ttk.Frame(setting_frm)
    text_frame.grid(row=0, column=1, rowspan=3, padx=100, pady=10, sticky="nsew")

    # Industry Button
    industry_button = ttk.Button(setting_frm, text="Add industry", width=30, command=on_industry_click)
    industry_button.grid(row=0, column=0, pady=63, sticky="w")

    # Job Title Button
    jobtitle_button = ttk.Button(setting_frm, text="Add job title", width=30, command=on_jobtitle_click)
    jobtitle_button.grid(row=1, column=0, pady=63, sticky="w")

    # Location Button
    location_button = ttk.Button(setting_frm, text="Add location", width=30, command=on_location_click)
    location_button.grid(row=2, column=0, pady=63, sticky="w")
    root_setting.protocol("WM_DELETE_WINDOW", lambda: [root_setting.destroy(), reload_dropdowns()])
    root_setting.mainloop()  # Start the event loop

def add_to_textbox(textbox, dropdown):
    """Add the selected dropdown item to the textbox."""
    selected_item = dropdown.get()
    textbox_values = textbox.get("1.0", "end-1c").strip()  
    
    if selected_item:
        if selected_item in textbox_values:
            print("Already in textbox")
        else:
            # Insert the selected item into the textbox with a comma and newline
            textbox.insert(END, f"{selected_item}\n")
            # Clear the dropdown selection
            dropdown.set("")
    else:
        print("No item selected from dropdown")

def read_file(filename):
    """Read file contents and return as a list of strings."""
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File {filename} not found.")
        messagebox.showerror("File Not Found",f"File {filename} not found.")
        return []

# This is for the confirmation windows 
def confirm_window():

    if not job_titles_value or not location_value or not industry_value:
        messagebox.showwarning(
            "Warning",
            "Please make sure all fields are not empty."
        )
    else:
        job_string = "\n".join(job_titles_value)
        location_string = "\n".join(location_value)
        industry_string = "\n".join(industry_value)
 
        message = f"**Job Title** : \n{job_string}\n\n**Location** : \n{location_string}\n\n**Industry** : \n{industry_string}"

        # Display a messagebox with Yes and No buttons
        response = messagebox.askyesno("Confirm Action", f"Do you want to proceed with the details below?\n\n{message}")
    
        # Check the user's response
        if response:  # If Yes was clicked
            print("User clicked Yes")
            # You can add code here to perform the action on "Yes"
        else:  # If No was clicked
            print("User clicked No")
            # You can add code here to perform the action on "No"

def on_text_change(text_type):
    global location_value, industry_value, job_titles_value
    global previous_text1, previous_text2, previous_text3

    new_text1 = job_titles_textbox.get("1.0", "end-1c").strip()
    new_text2 = location_textbox.get("1.0", "end-1c").strip()
    new_text3 = industries_textbox.get("1.0", "end-1c").strip()

    if (new_text1 != previous_text1) or (new_text2 != previous_text2) or (new_text3 != previous_text3):
        if text_type == "Job Titles" and new_text1 != previous_text1:
            temp_list = [item.strip() for item in new_text1.split("\n") if item.strip()]
            job_titles_value = temp_list
            previous_text1 = new_text1
        elif text_type == "Location" and new_text2 != previous_text2:
            temp_list = [item.strip() for item in new_text2.split("\n") if item.strip()]
            location_value = temp_list
            previous_text2 = new_text2
        elif text_type == "Industries" and new_text3 != previous_text3:
            temp_list = [item.strip() for item in new_text3.split("\n") if item.strip()]
            industry_value = temp_list
            previous_text3 = new_text3
        else:
            print("Bug")
    
    # Reset the modified state to allow the event to fire again
    job_titles_textbox.edit_modified(False)
    location_textbox.edit_modified(False)
    industries_textbox.edit_modified(False)
    
root = Tk()
# Configure window's height and width
window_height = 600
window_width = 1270
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.resizable(False, False)

# Make the root window's grid expandable
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Use ttk.Frame with the correct import
frm = ttk.Frame(root, padding=20)
frm.grid(column=0, row=0, sticky="nsew")

# Add labels
ttk.Label(frm, text="Select Job Titles").grid(column=0, row=0, pady=0, padx=100, sticky="w")
ttk.Label(frm, text="Select Location").grid(column=1, row=0, pady=0, padx=130, sticky="w")
ttk.Label(frm, text="Select Industry & Keywords").grid(column=2, row=0, pady=0, padx=100, sticky="w")

# Add textboxes with scrollbars
# Job Titles
job_titles_frame = ttk.Frame(frm)
job_titles_frame.grid(row=1, column=0, sticky="w", padx=15, pady=5)
job_titles_textbox = Text(job_titles_frame, width=30, height=4, wrap="word")
job_titles_textbox.pack(side=LEFT, fill=BOTH, expand=True)
job_titles_scrollbar = ttk.Scrollbar(job_titles_frame, orient=VERTICAL, command=job_titles_textbox.yview)
job_titles_scrollbar.pack(side=RIGHT, fill=Y)
job_titles_textbox.config(yscrollcommand=job_titles_scrollbar.set)

# Location
location_frame = ttk.Frame(frm)
location_frame.grid(row=1, column=1, sticky="w", padx=25, pady=5)
location_textbox = Text(location_frame, width=30, height=4, wrap="word")
location_textbox.pack(side=LEFT, fill=BOTH, expand=True)
location_scrollbar = ttk.Scrollbar(location_frame, orient=VERTICAL, command=location_textbox.yview)
location_scrollbar.pack(side=RIGHT, fill=Y)
location_textbox.config(yscrollcommand=location_scrollbar.set)

# Industries
industries_frame = ttk.Frame(frm)
industries_frame.grid(row=1, column=2, sticky="w", padx=30, pady=5)
industries_textbox = Text(industries_frame, width=30, height=4, wrap="word")
industries_textbox.pack(side=LEFT, fill=BOTH, expand=True)
industries_scrollbar = ttk.Scrollbar(industries_frame, orient=VERTICAL, command=industries_textbox.yview)
industries_scrollbar.pack(side=RIGHT, fill=Y)
industries_textbox.config(yscrollcommand=industries_scrollbar.set)

# Bind the <<Modified>> event to detect changes in the Textbox, fires when there is a change
previous_text1 = job_titles_textbox.get("1.0", "end-1c").strip()  
previous_text2 = location_textbox.get("1.0", "end-1c").strip()  
previous_text3 = industries_textbox.get("1.0", "end-1c").strip()  
job_titles_textbox.bind("<<Modified>>", lambda event: on_text_change("Job Titles"))
location_textbox.bind("<<Modified>>", lambda event: on_text_change("Location"))
industries_textbox.bind("<<Modified>>", lambda event: on_text_change("Industries"))

# Read dropdown options from files
job_titles = read_file("jobtitle.txt")
locations = read_file("location.txt")
industries = read_file("industry.txt")

# Add dropdown menus and buttons
# Dropdown for Job Titles
job_titles_dropdown = ttk.Combobox(frm, values=job_titles, state="readonly", width=29)
job_titles_dropdown.grid(row=2, column=0, pady=10, padx=15, sticky="w")
job_titles_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(job_titles_textbox, job_titles_dropdown))
job_titles_add_button.grid(row=2, column=0, pady=10, padx=(280, 0), sticky="e")

# Dropdown for Locations
location_dropdown = ttk.Combobox(frm, values=locations, state="readonly", width=29)
location_dropdown.grid(row=2, column=1, pady=10, padx=25, sticky="w")
location_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(location_textbox, location_dropdown))
location_add_button.grid(row=2, column=1, pady=10, padx=(290, 0), sticky="e")

# Dropdown for Industries
industries_dropdown = ttk.Combobox(frm, values=industries, state="readonly", width=29)
industries_dropdown.grid(row=2, column=2, pady=10, padx=30, sticky="w")
industries_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(industries_textbox, industries_dropdown))
industries_add_button.grid(row=2, column=2, pady=10, padx=(300, 0), sticky="e")

# Add a setting button to invoke Setting windows 
setting_image = Image.open("setting.png")  # Load the image
setting_image = setting_image.resize((40, 40))  # Resize the image (corrected line)
setting_image_tk = ImageTk.PhotoImage(setting_image)  # Convert to Tkinter-compatible format

setting_button = Button(root, image=setting_image_tk,command=setting)  # Create the button with the image
setting_button.grid(row=3, column=2, pady=20, padx=20, sticky="se")  # Place the button

# Confirm button after selecting values
confirm_button = ttk.Button(root, text="Confirm", command=confirm_window)
confirm_button.grid(row=3, column=0, pady=10, padx=(600, 0), sticky="w")

# Keep a reference to the image to prevent it from being garbage collected
setting_button.image = setting_image_tk


root.mainloop()