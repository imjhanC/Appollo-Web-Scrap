from tkinter import *
from tkinter import ttk  # Correctly import ttk for themed widgets

def add_to_textbox(textbox, dropdown):
    """Add the selected dropdown item to the textbox."""
    selected_item = dropdown.get()
    if selected_item:
        textbox.insert(END, f"{selected_item}\n")
        dropdown.set("")  # Clear the dropdown selection

root = Tk()
# Configure window's height and width
window_height = 600
window_width = 1240
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
frm = ttk.Frame(root, padding=50)
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

# Add dropdown menus and buttons
# Dropdown for Job Titles
job_titles_dropdown = ttk.Combobox(frm, values=["Software Engineer", "Data Scientist", "Product Manager"], state="readonly", width=29)
job_titles_dropdown.grid(row=2, column=0, pady=10, padx=15, sticky="w")
job_titles_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(job_titles_textbox, job_titles_dropdown))
job_titles_add_button.grid(row=2, column=0, pady=10, padx=(280, 0), sticky="e")

# Dropdown for Locations
location_dropdown = ttk.Combobox(frm, values=["New York", "San Francisco", "London"], state="readonly", width=29)
location_dropdown.grid(row=2, column=1, pady=10, padx=25, sticky="w")
location_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(location_textbox, location_dropdown))
location_add_button.grid(row=2, column=1, pady=10, padx=(290, 0), sticky="e")

# Dropdown for Industries
industries_dropdown = ttk.Combobox(frm, values=["Tech", "Finance", "Healthcare"], state="readonly", width=29)
industries_dropdown.grid(row=2, column=2, pady=10, padx=30, sticky="w")
industries_add_button = ttk.Button(frm, text="Add", command=lambda: add_to_textbox(industries_textbox, industries_dropdown))
industries_add_button.grid(row=2, column=2, pady=10, padx=(300, 0), sticky="e")

root.mainloop()
