# seleniumCalpads
A selenium based python program designed to automatically navigate through calpads to download the reports from them
- The github for this project can be found [here](https://github.com/6WeinsteinJ/seleniumCalpads)

# Prerequisites
- You will need to have [python](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/) installed
- Install selenium through `pip install selenium`
- Install customtkinter through `pip3 install customtkinter`

# How To Change the School Data
1. Navigate to the school_data.json file in an editor
2. To add a school, add a comma after the last element input the full **14 digit** LEA code in quotation marks followed by a colon and then the school name in quotation marks.
Ex: `"00000000000000": "My School Name"`

# How To Package (.exe)
1. Download pyinstaller through the command `pip install -U pyinstaller`
2. Open up the Command Prompt
3. Navigate to the directory where the code is downloaded (tutorial on how to use cd [here](https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/ )
4. Find the location of the customtkinter package by typing in `pip show customtkinter` in the terminal and look under location
5. Type the following command into the command prompt `pyinstaller --onefile --add-data "school_data.json;." --add-data "[CUSTOMTKINTER LOCATION]"/customtkinter;customtkinter/" --add-binary "src/driver/chromedriver.exe;./driver" cli.py`
6. The exe file will be located in the file named *dist* in the directory where the code was downloaded

#
# Known Issues
- CALPADS sometimes has invalid sessions which will the program can't detect,
- Trying to change the year after generating the report periods requires generating the periods again, otherwise the desired reports may be different
- The same school can be selected more than once

# Updating Chromedriver
- Chromedriver can be updated by downloading all of the code and going to src -> driver -> and switching out the chromedriver.exe file with the new file


