from cx_Freeze import setup, Executable
import sys

# Dependencies
build_exe_options = {
    "packages": ["tkinter", "pandas", "undetected_chromedriver", "selenium", "fake_useragent"],
    "includes": [],
    "include_files": ["icon.ico"],  # Include your icon file
    "excludes": []
}

# Set the base
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this for GUI applications to suppress the console

# Define the executable
executables = [
    Executable(
        script="apollo.py",  # Your script name
        base=base,
        target_name="Apollo.exe",  # Output EXE name
        icon="icon.ico"  # Path to your icon
    )
]

# Setup function
setup(
    name="Apollo",
    version="1.0",
    description="Apollo Application",
    options={"build_exe": build_exe_options},
    executables=executables
)
