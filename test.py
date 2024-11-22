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

def setting():
    root_setting = Toplevel(root) # <--- (note) This code is to keep the windows on top of another windows 
    window_width = 1270
    window_height = 600
    screen_width = root_setting.winfo_screenwidth()  # Add parentheses to call the method
    screen_height = root_setting.winfo_screenheight()  # Add parentheses to call the method
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root_setting.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root_setting.resizable(False, False)
    root_setting.columnconfigure(0, weight=1)
    root_setting.rowconfigure(0, weight=1)
    root_setting.transient(root) # <--- (note) This code is to keep the windows on top of another windows 
    root_setting.grab_set()  # <--- (note) This code is to keep the windows on top of another windows 
    root_setting.mainloop()  # Call the method

def add_to_textbox(textbox, dropdown):
    """Add the selected dropdown item to the textbox."""
    selected_item = dropdown.get()
    
    if selected_item:
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
 
        message = f"Job Title: {job_string}\n\nLocation: {location_string}\n\nIndustry: {industry_string}"

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