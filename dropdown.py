from tkinter import *
import tkinter as tkk

# Create object 
root = Tk() 
  
# Adjust size 
# Window size and positioning
window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2 
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.resizable(True, True)


  
# Change the label text 
def show(): 
    label.config( text = clicked.get() ) 
  
# Dropdown menu options 
options = [ 
    "Monday", 
    "Tuesday", 
    "Wednesday", 
    "Thursday", 
    "Friday", 
    "Saturday", 
    "Sunday"
] 
  
# datatype of menu text 
clicked = StringVar() 
  
# initial menu text 
clicked.set( "Monday" ) 
  
# Create Dropdown menu 
drop = OptionMenu( root , clicked , *options ) 
drop.grid()
  
# Create button, it will change label text 
button = Button( root , text = "click Me" , command = show ).pack() 
  
# Create Label 
label = Label( root , text = " " ) 
label.pack() 
  
# Execute tkinter 
root.mainloop() 