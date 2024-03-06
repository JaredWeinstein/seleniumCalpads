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

# Updating Chromedriver
- The chromedriver download can be obtained from [this](https://chromedriver.chromium.org/) link
- Chromedriver can be updated by downloading all of the code and going to src -> driver -> and switching out the chromedriver.exe file with the new file

# How To Package (.exe)
1. Most of the package downloads will be done through the anaconda (https://conda.io/projects/conda/en/latest/index.html) environment, which can be downloaded through the link
2. Open up the conda environment by searching Anaconda in the search bar and clicking on it
3. Most of the instructions typed below will be pulled from [this](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment) link
5. In the conda environment, type `conda create --name my_env` (Most of the commands will require typing `y` after to confirm)
6. After creating it, type `conda activate my_env`, which will have to be retyped if you ever close and reopen the program
7. Install pip in the environment by typing `conda install pip`
8. Download pyinstaller through the command `pip install -U pyinstaller`
9. Download customtkinter through the command `pip install customtkinter`
10. Download selenium (if you haven't done so yet) through `pip install selenium`
11. Navigate to the directory where the code is downloaded which is where the src, README, and schooldata.json file are located (You can check by typing `dir` and seeing if these files are present)
(tutorial on how to use cd [here](https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/ )
12. Find the location of the customtkinter package by typing in `pip show customtkinter` in the terminal and look under location  as seen below ![image](https://github.com/JaredWeinstein/seleniumCalpads/assets/54867509/f7b198e5-d00f-4810-9291-acf0668381e0)
13. Type the following command into the command prompt `pyinstaller --onefile --add-data "school_data.json;." --add-data "[YOUR CUSTOMTKINTER LOCATION]/customtkinter;customtkinter/" --add-binary "src/driver/chromedriver.exe;./driver" cli.py`
14.  The exe file will be located in the file named *dist* in the directory where the code was downloaded



# Known Issues
- CALPADS sometimes has invalid sessions which will the program can't detect,
- Trying to change the year after generating the report periods requires generating the periods again, otherwise the desired reports may be different
- The same school can be selected more than once



