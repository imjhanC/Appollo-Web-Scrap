from tkinter import * 
from tkinter import ttk, messagebox # Correctly import ttk for themed widgets
from PIL import Image, ImageTk

def setting():
    root_setting = Toplevel(root)
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
    root_setting.transient(root)
    root_setting.grab_set()
    root_setting.mainloop()  # Call the method


def add_to_textbox(textbox, dropdown):
    """Add the selected dropdown item to the textbox."""
    selected_item = dropdown.get()
    if selected_item:
        textbox.insert(END, f"{selected_item},\n")
        dropdown.set("")  # Clear the dropdown selection

def read_file(filename):
    """Read file contents and return as a list of strings."""
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File {filename} not found.")
        messagebox.showerror("File Not Found",f"File {filename} not found.")
        return []

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

# Keep a reference to the image to prevent it from being garbage collected
setting_button.image = setting_image_tk


root.mainloop()