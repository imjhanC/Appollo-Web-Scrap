from cx_Freeze import setup, Executable

setup(
    name="Leads Scraping Application",
    version="1.0",
    description="Your application description",
    executables=[Executable("apollo.py")],  # Replace main.py with your script name
)
