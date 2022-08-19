# seleniumCalpads
A selenium based python program designed to automatically navigate through calpads to download the reports from them


# Prerequisites
- You will need to have [python](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/) installed

# Installation Guide
Recommended to install through `pip install git+https://github.com/6WeinsteinJ/seleniumCalpads.git`

# How To Change the School Data
1. Navigate to the school_data.json file in an editor
2. To add a school, add a comma after the last element input the full **14 digit** LEA code in quotation marks followed by a colon and then the school name in quotation marks.
Ex: `"00000000000000": "My School Name"`


# How To Package (.exe)
1. Download pyinstaller through the command `pip install -U pyinstaller`
2. Open up the Command Prompt
3. Navigate to the directory where the code is downloaded (tutorial on how to use cd [here](https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/)
4. Type the following command into the command prompt `pyinstaller --onefile --add-data "school_data.json;." --add-data "c:/users/blueb/appdata/local/programs/python/python310/lib/site-packages/customtkinter;customtkinter/" --add-binary "src/driver/chromedriver.exe;./driver" cli.py`
5. The exe file will be located in the file named *dist* in the directory where the code was downloaded
