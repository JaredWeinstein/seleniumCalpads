# seleniumCalpads
A selenium based python program designed to automatically navigate through calpads to download the reports from them

#How To Package (.exe)
1. Download pyinstaller through the command `pip install -U pyinstaller`




pyinstaller --onefile --add-data "school_data.json;." --add-data "c:/users/blueb/appdata/local/programs/python/python310/lib/site-packages/customtkinter;customtkinter/" --add-binary "src/driver/chromedriver.exe;./driver" cli.py

# Installation Guide
Recommended to install through `pip install git+https://github.com/6WeinsteinJ/seleniumCalpads.git`
