import sys
import tkinter
import tkinter.ttk as ttk
from threading import Thread
from tkinter import *
from tkinter import filedialog
from src.cert_reports import Browser
from tkinter import messagebox
import json
import os


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


school = []
json_file_path = resource_path('school_data.json')
with open(json_file_path, 'r') as j:
    school_data = json.loads(j.read())
for i in school_data.keys():
    school.append(school_data[i] + " - " + i[-7:])
school.sort()


class Window:

    def __init__(self):
        self.curr_link = None
        self.curr_school = None
        self.browser = None

        def check(event):
            value = event.widget.get()
            if value == '':
                data = school[0:400]
            else:
                data = []
            counter = 0
            for item in school:
                if counter > 400:
                    break
                if value.lower() in item.lower():
                    data.append(item)
                    counter += 1
            update(data)

        def update(data):
            # Clear the Combobox
            self.l_list.delete(0, END)
            # Add values to the combobox
            for value in data:
                self.l_list.insert(END, value)

        self.curr_pass = ""
        self.curr_user = ""
        self.curr_year = ""
        self.curr_term = ""
        self.curr_folder = ""
        self.curr_file_type = ""
        self.selected_schools = []
        self.link_list = []
        self.dry_run = False

        window = Tk()
        window.geometry("900x650")
        window.title("CALPADS report fetcher")
        self.window = window

        part_one = LabelFrame(window, width=890, height=430, text="Part 1", borderwidth=5)
        part_one.pack()
        part_two = LabelFrame(window, width=890, height=210, text="Part 2", borderwidth=5)
        part_two.pack()

        # Widgets related to the user's username
        u_label = Label(window, text="Calpads Username:")
        u_label.place(x=20, y=20)
        self.u_box = Entry(window, width=35)
        self.u_box.place(x=180, y=20)

        # Widgets related to the user's password
        p_label = Label(window, text="Calpads Password:")
        p_label.place(x=21, y=60)
        self.p_box = Entry(window, show="*", width=35)
        self.p_box.place(x=180, y=60)

        # Widgets relating to the lea code/school
        l_label = Label(window, text="Search for and select the \n LEA Code/School  from the list:")
        l_label.place(x=15, y=110)
        self.l_box = Entry(window, width=40)
        self.l_box.bind('<KeyRelease>', check)
        self.l_box.place(x=200, y=110)
        self.l_list = Listbox(window, width=50, selectmode=SINGLE)
        self.l_list.configure(exportselection=False)
        self.l_list.place(x=200, y=140)
        update(school)

        current_l_label = Label(window, text="Currently Selected Schools")
        current_l_label.place(x=625,y=110)
        self.add_lea = Button(window, text="Add selected school", command=lambda: self.add_school())
        self.add_lea.place(x=300, y=320)
        self.current_l_list = Listbox(window, width=50, selectmode=SINGLE)
        self.current_l_list.configure(exportselection=False)
        self.current_l_list.place(x=550, y=140)
        current_l_remove = Button(window, text="Remove selected school", command=lambda: self.remove_school())
        current_l_remove.place(x=625, y=320)

        # Widgets relating to the report year
        y_label = Label(window, text="Report year:")
        y_label.place(x=550, y=40)
        self.year = StringVar()
        self.year.set('Please choose the year')
        y_list = ttk.Combobox(self.window, textvariable=self.year)
        y_list['values'] = ["2022-2023", "2021-2022", "2020-2021", "2019-2020", "2018-2019", "2017-2018", "2016-2017",
                            "2015-2016"]
        y_list.place(x=650, y=40)

        self.dry_run_button = Button(window, text="Generate all report periods\n for selected year", command=lambda: self.submit_dry_run(),
                                bg="GreenYellow")
        self.dry_run_button.place(x=30, y=375)

        # Widgets relating to the term
        t_label = Label(window, text="Which report period?")
        t_label.place(x=100, y=460)
        self.term = StringVar()
        self.term.set("Select a Term")
        self.t_list = OptionMenu(window, self.term, "Select a Term")
        self.t_list['state'] = "disabled"
        self.t_list.place(x=220, y=455)

        # Widgets related to the file type
        file_type_label = Label(window, text="Choose what type of \n file to be exported:")
        file_type_label.place(x=475, y=450)
        self.file_type = StringVar()
        self.file_type.set("Select file type")
        self.file_type_list = OptionMenu(window, self.file_type, 'PDF', 'EXCEL', 'CSV')
        self.file_type_list['state'] = "disabled"
        self.file_type_list.place(x=600, y=455)

        # Widgets related to the folder of the downloads
        self.folder_path = StringVar()
        self.folder_button = Button(window, text="File selector", command=lambda: self.dir_searcher(), state=DISABLED)
        self.folder_button.place(x=300, y=530)
        folder_label = Label(window, text="Select a folder for the downloads: \n (This app will create a new folder)")
        folder_label.place(x=100, y=530)
        self.current_location = Label(window, textvariable=self.folder_path)
        self.current_location.place(x=450, y=530)

        self.submit = Button(window, text="Submit new data", command=lambda: self.submit_press(), bg="GreenYellow",
                             state=DISABLED)
        self.submit.place(x=50, y=600)

        self.resubmit = Button(window, text="Resume downloading?", command=lambda: self.resubmit_press(),
                               bg="GreenYellow")

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                window.destroy()
                if self.browser is not None:
                    self.browser.close_browser()
                    quit()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()

    def destroy_window(self):
        self.window.destroy()

    def submit_dry_run(self):
        if self.year.get() == 'Please choose the year' or self.u_box.get() == "" \
                or self.p_box.get() == "" or len(self.selected_schools) == 0:
            messagebox.showerror("Error", "Please input data for every field")
            return
        self.curr_user = self.u_box.get()
        self.curr_pass = self.p_box.get()
        self.curr_year = self.year.get()
        self.dry_run = True
        self.dry_run_button['state'] = 'disabled'

        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()

    def update_term(self, term_list):
        self.link_list = term_list.values()
        temp_list = list(term_list.keys())
        self.t_list = OptionMenu(self.window, self.term, *temp_list)
        self.t_list.place(x=220, y=455)
        self.t_list['state'] = 'normal'
        self.file_type_list['state'] = 'normal'
        self.folder_button['state'] = 'normal'
        self.submit['state'] = 'normal'
        self.dry_run_button['state'] = 'normal'

    def submit_press(self):
        if self.year.get() == 'Please choose the year' or self.term.get() == "Select a Term" or self.u_box.get() == "" \
                or self.p_box.get() == "" or len(self.selected_schools) == 0 or self.folder_path.get() == "" \
                or self.file_type.get() == "Select file type":
            messagebox.showerror("Error", "Please input data for every field")
            return
        self.curr_user = self.u_box.get()
        self.curr_pass = self.p_box.get()
        self.curr_term = self.term.get()
        self.curr_year = self.year.get()
        self.curr_file_type = self.file_type.get()
        self.submit['state'] = "disabled"
        self.dry_run = False
        self.curr_link = None
        self.curr_school = None
        new_dir = os.path.join(self.folder_path.get(), self.year.get() + " " + self.term.get())
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        self.curr_folder = new_dir
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()

    def remove_school(self):
        if len(self.current_l_list.curselection()) != 0:
            self.selected_schools.remove(self.current_l_list.get(self.current_l_list.curselection()))
            idx = self.current_l_list.get(0, tkinter.END).index(self.current_l_list.get(self.current_l_list.curselection()))
            self.current_l_list.delete(idx)

    def add_school(self):
        if len(self.l_list.curselection()) != 0:
            self.selected_schools.append(self.l_list.get(self.l_list.curselection()))
            self.current_l_list.insert(tkinter.END, self.l_list.get(self.l_list.curselection()))

    def enable_button(self):
        self.submit['state'] = "normal"

    def dir_searcher(self):
        filename = filedialog.askdirectory()
        self.folder_path.set(filename)
        self.current_location['text'] = ("The current download location is: " + self.folder_path.__str__())

    def browser_create(self):
        self.browser = Browser(self.curr_user, self.curr_pass, self.selected_schools, self.curr_term, self.curr_year,
                               self.curr_folder, self.curr_file_type, self, self.curr_school, self.curr_link)
        self.browser.run_browser(self.dry_run)

    def quit_program(self):
        self.window.quit()

    def get_browser_info(self, curr_school, link):
        self.submit['state'] = "normal"
        self.resubmit['state'] = "normal"
        if curr_school is not None:
            print("browser info saved")
            self.resubmit.place(x=200, y=600)
            self.curr_link = link
            self.curr_school = curr_school

    def resubmit_press(self):
        self.submit['state'] = "disabled"
        self.resubmit['state'] = "disabled"
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()
