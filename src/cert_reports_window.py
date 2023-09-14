import sys
import tkinter
from threading import Thread
from tkinter import *
import customtkinter
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

# Scuffed af way of sorting the reports cause they're in a weird format lmao
def special_sort(e):
    num = e.split()[0]
    separated_nums = num.split(".")
    if not separated_nums[0].isnumeric():
        f_num = float(separated_nums[0][:-1]) * 10000 + ord(separated_nums[0][-1])
    else:
        f_num = int(separated_nums[0]) * 10000

    if not separated_nums[1].isnumeric():
        if "-" in separated_nums[1]:
            separated_nums[1] = separated_nums[1].split("-")[0]
        if len(separated_nums[1]) > 1:
            s_num = float(separated_nums[1][:-1]) + float(ord(separated_nums[1][-1]) / 100)
        else:
            s_num = int(separated_nums[1])
    else:
        s_num = int(separated_nums[1])

    return f_num + s_num


class Window:
    customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
    customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

    def __init__(self):
        self.curr_data = [None, None, None]
        self.browser = None

        window = customtkinter.CTk(fg_color="#8bb586")
        window.geometry("925x725")
        window.title("CALPADS report fetcher")
        window.resizable(False, False)
        self.window = window
        self.term = customtkinter.StringVar()

        # Checks if there is an update in the Entry Box
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

        # Updates the listbox values
        def update(data):
            # Clear the Combobox
            self.l_list.delete(0, END)
            # Add values to the combobox
            for value in data:
                self.l_list.insert(END, value)

        self.curr_pass = ""
        self.curr_user = ""
        self.curr_year = ""
        self.curr_folder = ""
        self.selected_schools = []
        self.link_list = []
        self.dry_run = False
        self.reports_list = {}
        self.cert_reports = {}
        self.pdf_reports = []
        self.csv_reports = []
        self.excel_reports = []
        self.report_count = 0

        part_one = customtkinter.CTkFrame(window, width=900, height=430, border_color="black", borderwidth=5,
                                          fg_color="#dff0dd")
        part_one.pack()
        self.step_two = customtkinter.CTkFrame(window, width=900, height=300, border_color="black", borderwidth=5,
                                               fg_color="#dff0dd")
        self.step_two.pack(fill=tkinter.BOTH, pady=15, padx=5)

        pt1_label = customtkinter.CTkLabel(window, text="Step 1", height=10, width=30, fg_color="#dff0dd",
                                           text_font='Avenir 15',
                                           text_color="black")
        pt1_label.place(x=25, y=7)
        self.pt2_label = customtkinter.CTkLabel(window, text="Step 2", height=10, width=30, fg_color="#dff0dd",
                                                text_font='Avenir 15',
                                                text_color="black")
        self.pt2_label.place(x=25, y=435)

        # Widgets related to the user's username
        u_label = customtkinter.CTkLabel(window, text="Calpads Username:", fg_color="#dff0dd")
        u_label.place(x=20, y=33)
        self.u_box = customtkinter.CTkEntry(window, width=200, bg_color="#dff0dd")
        self.u_box.place(x=180, y=33)

        # Widgets related to the user's password
        p_label = customtkinter.CTkLabel(window, text="Calpads Password:", fg_color="#dff0dd")
        p_label.place(x=21, y=70)
        self.p_box = customtkinter.CTkEntry(window, show="*", width=200, bg_color="#dff0dd")
        self.p_box.place(x=180, y=70)

        # Widgets relating to the lea code/school

        l_label = customtkinter.CTkLabel(window, fg_color="#dff0dd",
                                         text="Search for and select the \n LEA Code/School  from the list:")
        l_label.place(x=15, y=110)
        self.l_box = customtkinter.CTkEntry(window, width=225, bg_color="#dff0dd")
        self.l_box.bind('<KeyRelease>', check)
        self.l_box.place(x=200, y=110)
        listbox_frame = customtkinter.CTkFrame(part_one, width=325, height=170, fg_color="#dff0dd")
        listbox_frame.place(x=190, y=140)
        self.l_list = Listbox(listbox_frame, width=50, selectmode=SINGLE)
        self.l_list.configure(exportselection=False)
        self.l_list.place(x=0, y=0)
        update(school)

        current_l_label = customtkinter.CTkLabel(window, text="Currently Selected Schools", fg_color="#dff0dd")
        current_l_label.place(x=625, y=110)
        self.add_lea = customtkinter.CTkButton(window, text="Add selected school", command=lambda: self.add_school(),
                                               bg_color="#dff0dd")
        self.add_lea.place(x=300, y=320)
        clistbox_frame = customtkinter.CTkFrame(part_one, width=325, height=170, fg_color="#dff0dd")
        clistbox_frame.place(x=515, y=140)
        self.current_l_list = Listbox(clistbox_frame, width=50, selectmode=SINGLE)
        self.current_l_list.configure(exportselection=False)
        self.current_l_list.place(x=0, y=0)
        current_l_remove = customtkinter.CTkButton(window, text="Remove selected school",
                                                   command=lambda: self.remove_school(), bg_color="#dff0dd")
        current_l_remove.place(x=625, y=320)

        # Widgets relating to the report year
        y_label = customtkinter.CTkLabel(window, width=75, text="Report year:", fg_color="#dff0dd", bg_color="#dff0dd")
        y_label.place(x=550, y=38)
        self.year = customtkinter.StringVar()
        self.year.set('Please choose the year')
        y_list = customtkinter.CTkComboBox(self.window, variable=self.year, width=175, bg_color="#dff0dd",
                                           values=["2023-2024", "2022-2023", "2021-2022",
                                                   "2020-2021", "2019-2020",
                                                   "2018-2019", "2017-2018",
                                                   "2016-2017",
                                                   "2015-2016"])
        y_list.place(x=635, y=40)
        self.dry_run_button = customtkinter.CTkButton(window, text="Generate all report periods\n for selected year",
                                                      command=lambda: self.submit_dry_run(), bg_color="#dff0dd")
        self.dry_run_button.place(x=30, y=375)

        self.settings_f = customtkinter.CTkFrame(self.step_two, fg_color="#dff0dd")
        self.settings_f.pack(ipadx=10, ipady=10, fill=tkinter.BOTH, side=tkinter.LEFT, expand=True)
        self.reports_f = customtkinter.CTkFrame(self.step_two, fg_color="#dff0dd")
        self.reports_f.pack(ipadx=10, ipady=10, fill=tkinter.BOTH, side=tkinter.RIGHT, expand=True)

        # Widgets relating to the term
        t_label = customtkinter.CTkLabel(self.settings_f, fg_color="#dff0dd", text="Which report period?")
        t_label.grid(row=0, column=0, columnspan=2, sticky=W, padx=20, pady=10)
        self.term.set("Select a Term")
        self.t_list = customtkinter.CTkOptionMenu(self.settings_f, state="disabled", variable=self.term,
                                                  values=["Select a Term"], bg_color="#dff0dd",
                                                  command=self.update_report)
        self.t_list.grid(row=0, column=1, sticky=E, pady=10)

        # Widgets related to selecting the reports
        self.reports_display = Listbox(self.reports_f, selectmode=EXTENDED, width=60, height=12)
        self.reports_display.grid(row=0, column=0, padx=0, pady=(20, 0), sticky="nsew", rowspan=4)
        pdf_button = customtkinter.CTkButton(self.reports_f, text="Add \n as PDF", width=70,
                                             command=self.add_pdf_reports)
        pdf_button.grid(row=0, column=1, padx=5)
        excel_button = customtkinter.CTkButton(self.reports_f, text="Add \n as EXCEL", width=70,
                                               command=self.add_excel_reports)
        excel_button.grid(row=1, column=1, padx=5)
        csv_button = customtkinter.CTkButton(self.reports_f, text="Add \n as CSV", width=70,
                                             command=self.add_csv_reports)
        csv_button.grid(row=2, column=1, padx=5)
        view_button = customtkinter.CTkButton(self.reports_f, text="View Selected \n Reports",
                                              command=self.view_reports)
        view_button.grid(row=3, column=1, padx=5)

        self.reports_f.columnconfigure(0, weight=10)
        self.reports_f.columnconfigure(1, weight=1)

        # Widgets related to the folder of the downloads
        self.folder_path = customtkinter.StringVar()
        self.folder_button = customtkinter.CTkButton(self.settings_f, text="File selector",
                                                     command=lambda: self.dir_searcher(),
                                                     state=DISABLED, bg_color="#dff0dd", width=10)
        self.folder_button.grid(row=1, column=1, sticky=E, pady=10)
        folder_label = customtkinter.CTkLabel(self.settings_f, fg_color="#dff0dd",
                                              text="Select a folder for the downloads: \n (This app will create a new folder)")
        folder_label.grid(row=1, column=0, columnspan=2, sticky=W, padx=20, pady=10)
        self.current_location = customtkinter.CTkLabel(self.settings_f, textvariable=self.folder_path,
                                                       fg_color="#dff0dd")
        self.current_location.grid(row=2, column=0, columnspan=3, pady=0, padx=20, sticky="nsew")


        blank_row = customtkinter.CTkLabel(self.settings_f, text="", bg_color="#dff0dd", fg_color="#dff0dd")
        blank_row.grid(row=3)
        self.submit = customtkinter.CTkButton(self.settings_f, text="Submit new data",
                                              command=lambda: self.submit_press(),
                                              state="disabled", bg_color="#dff0dd")
        self.submit.grid(row=4, column=0, sticky=S, padx=20, pady=0)

        self.resubmit = customtkinter.CTkButton(self.settings_f, text="Resume downloading?",
                                                command=lambda: self.resubmit_press(), bg_color="#dff0dd")

        # Widgets on the report viewer page to allow reports to be removed
        self.viewer_f = customtkinter.CTkFrame(window, width=900, height=300, border_color="black", borderwidth=5,
                                               fg_color="#dff0dd")
        back_button = customtkinter.CTkButton(self.viewer_f, text="Return", bg_color="#dff0dd",
                                              command=self.return_press)
        pdf_label = customtkinter.CTkLabel(self.viewer_f, fg_color="#dff0dd", text="PDF")
        excel_label = customtkinter.CTkLabel(self.viewer_f, fg_color="#dff0dd", text="EXCEL")
        csv_label = customtkinter.CTkLabel(self.viewer_f, fg_color="#dff0dd", text="CSV")
        self.pdf_listbox = Listbox(self.viewer_f, selectmode=EXTENDED, width=45)
        self.excel_listbox = Listbox(self.viewer_f, selectmode=EXTENDED, width=45)
        self.csv_listbox = Listbox(self.viewer_f, selectmode=EXTENDED, width=45)
        pdf_remove_button = customtkinter.CTkButton(self.viewer_f, text="Remove Selected PDF reports",
                                                    bg_color="#dff0dd",
                                                    command=self.delete_pdf_reports)
        excel_remove_button = customtkinter.CTkButton(self.viewer_f, text="Remove Selected EXCEL reports",
                                                      bg_color="#dff0dd",
                                                      command=self.delete_excel_reports)
        csv_remove_button = customtkinter.CTkButton(self.viewer_f, text="Remove Selected CSV reports",
                                                    bg_color="#dff0dd",
                                                    command=self.delete_csv_reports)

        pdf_label.grid(row=0, column=1)
        excel_label.grid(row=0, column=2)
        csv_label.grid(row=0, column=3)
        self.pdf_listbox.grid(row=1, column=1)
        self.excel_listbox.grid(row=1, column=2)
        self.csv_listbox.grid(row=1, column=3)
        pdf_remove_button.grid(row=2, column=1)
        excel_remove_button.grid(row=2, column=2)
        csv_remove_button.grid(row=2, column=3)
        back_button.grid(row=4, column=0)
        self.viewer_f.rowconfigure(0, weight=1)
        self.viewer_f.rowconfigure(1, weight=6)
        self.viewer_f.rowconfigure(2, weight=1)
        self.viewer_f.rowconfigure(3, weight=1)
        self.viewer_f.columnconfigure(0, weight=2)
        self.viewer_f.columnconfigure(0, weight=7)
        self.viewer_f.columnconfigure(0, weight=7)
        self.viewer_f.columnconfigure(0, weight=7)

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                window.destroy()
                if self.browser is not None:
                    self.browser.close_browser()
                    quit()
                else:
                    quit()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()

    # Method to destroy the window
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
        self.curr_data = [None, None, None]
        self.dry_run = True
        self.dry_run_button.configure(state="disabled")
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()

    def update_term(self, term_list, cert_reports):
        self.cert_reports = cert_reports
        # self.term list is in the format of [term] + "-" + Certification status
        temp_list = list(term_list.keys())
        self.t_list.configure(values=temp_list)
        self.t_list.configure(state="normal")
        self.t_list.grid(row=0, column=1, sticky=E, pady=10)
        self.folder_button.configure(state="normal")
        self.submit.configure(state="normal")
        self.dry_run_button.configure(state="normal")

    def submit_press(self):
        if self.year.get() == 'Please choose the year' or self.u_box.get() == "" \
                or self.p_box.get() == "" or len(self.selected_schools) == 0 or self.folder_path.get() == "" \
                or (len(self.csv_reports) == 0 and self.pdf_reports == 0 and self.excel_reports == 0):
            messagebox.showerror("Error", "Please input data for every field")
            return
        self.curr_user = self.u_box.get()
        self.curr_pass = self.p_box.get()
        self.dry_run_button.configure(state="disabled")
        self.submit.configure(state="disabled")
        self.dry_run = False
        self.curr_data = [None, None, None]

        self.pdf_reports.sort()
        self.excel_reports.sort()
        self.csv_reports.sort()
        self.report_count = 0
        # Puts the data for the reports (term, name, and file type) into a dictionary
        self.reports_list.clear()
        for pdf_report in self.pdf_reports:
            report_data = pdf_report.split("-")
            term = report_data[0]
            name = report_data[1]
            if self.reports_list.get(term) is None:
                self.reports_list[term] = []
            self.reports_list[term].append((name, "pdf"))
            self.report_count += 1
        for excel_report in self.excel_reports:
            report_data = excel_report.split("-")
            term = report_data[0]
            name = report_data[1]
            if self.reports_list.get(term) is None:
                self.reports_list[term] = []
            self.reports_list[term].append((name, "excel"))
            self.report_count += 1
        for csv_report in self.csv_reports:
            report_data = csv_report.split("-")
            term = report_data[0]
            name = report_data[1]
            if self.reports_list.get(term) is None:
                self.reports_list[term] = []
            self.reports_list[term].append((name, "csv"))
            self.report_count += 1
        self.report_count *= len(self.selected_schools)
        # Makes a new folder for every term that exists
        year_dir = os.path.join(self.folder_path.get(), self.year.get())
        if not os.path.exists(year_dir):
            os.mkdir(year_dir)
        self.curr_folder = year_dir
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()

    def browser_create(self):
        self.browser = Browser(self.curr_user, self.curr_pass, self.selected_schools, self.curr_year,
                               self.curr_folder, self, self.curr_data, self.reports_list, self.report_count)
        self.browser.run_browser(self.dry_run)

    def remove_school(self):
        """
        removes the school that is selected in the current schools listbox
        """
        if len(self.current_l_list.curselection()) != 0:
            self.selected_schools.remove(self.current_l_list.get(self.current_l_list.curselection()))
            idx = self.current_l_list.get(0, tkinter.END).index(
                self.current_l_list.get(self.current_l_list.curselection()))
            self.current_l_list.delete(idx)

    def add_school(self):
        """
        Adds the school that is selected in the listbox to the current schools listbox
        """
        if len(self.l_list.curselection()) != 0:
            self.selected_schools.append(self.l_list.get(self.l_list.curselection()))
            self.current_l_list.insert(tkinter.END, self.l_list.get(self.l_list.curselection()))

    def enable_button(self):
        self.submit.configure(state="normal")
        self.dry_run_button.configure(state="normal")
        self.resubmit.configure(state="normal")

    def hide_resubmit(self):
        self.resubmit.configure(state="disabled")

    def dir_searcher(self):
        filename = filedialog.askdirectory()
        self.folder_path.set(filename)
        self.current_location['text'] = ("The current download location is: " + self.folder_path.__str__())

    def quit_program(self):
        self.window.quit()

    def get_browser_info(self, curr_data, report_count):
        """
        Gets the information of the current school/link that the program was on in the event of CALPADS crashing
        or something weird happening
        """
        self.submit.configure(state="normal")
        self.resubmit.configure(state="normal")
        self.dry_run_button.configure(state="normal")
        self.report_count = report_count
        if curr_data[0] is not None:
            print("browser info saved")
            self.resubmit.grid(row=4, column=1, sticky=S, padx=20, pady=0)
            self.curr_data = curr_data

    def resubmit_press(self):
        self.submit.configure(state="disabled")
        self.resubmit.configure(state="disabled")
        self.dry_run_button.configure(state="disabled")
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()

    def update_report(self, event):
        term = self.term.get()
        if term != "Select a Term":
            all_reports_list = self.cert_reports[term]
            all_reports_list.sort(key=special_sort)
            self.reports_display.delete(0, END)
            for reports in all_reports_list:
                self.reports_display.insert(END, reports)

    def add_pdf_reports(self):
        reports = self.reports_display.curselection()
        if len(reports) != 0:
            for r in reports:
                term = (self.term.get().split("-"))[0][0:-1]
                temp = term + "-" + self.reports_display.get(r)
                if self.pdf_reports.count(temp) == 0:
                    self.pdf_reports.append(temp)

    def add_excel_reports(self):
        reports = self.reports_display.curselection()
        if len(reports) != 0:
            for r in reports:
                term = (self.term.get().split("-"))[0][0:-1]
                temp = term + "-" + self.reports_display.get(r)
                if self.excel_reports.count(temp) == 0:
                    self.excel_reports.append(temp)

    def add_csv_reports(self):
        reports = sorted(self.reports_display.curselection(), reverse=True)
        if len(reports) != 0:
            for r in reports:
                term = (self.term.get().split("-"))[0][0:-1]
                temp = term + "-" + self.reports_display.get(r)
                if self.csv_reports.count(temp) == 0:
                    self.csv_reports.append(temp)

    def delete_pdf_reports(self):
        selected = sorted(self.pdf_listbox.curselection(), reverse=True)
        if len(selected) != 0:
            for s in selected:
                self.pdf_reports.remove(self.pdf_listbox.get(s))
                self.pdf_listbox.delete(s)
        print(self.pdf_reports)

    def delete_excel_reports(self):
        selected = sorted(self.excel_listbox.curselection(), reverse=True)
        if len(selected) != 0:
            for s in selected:
                self.excel_reports.remove(self.excel_listbox.get(s))
                self.excel_listbox.delete(s)
        print(self.excel_reports)

    def delete_csv_reports(self):
        selected = sorted(self.csv_listbox.curselection(), reverse=True)
        if len(selected) != 0:
            for s in selected:
                self.csv_reports.remove(self.csv_listbox.get(s))
                self.csv_listbox.delete(s)
        print(self.csv_reports)

    def view_reports(self):
        self.step_two.pack_forget()
        self.viewer_f.pack(fill=tkinter.BOTH, pady=15, padx=5)
        self.pt2_label.lift()
        self.csv_listbox.delete(0, END)
        self.pdf_listbox.delete(0, END)
        self.excel_listbox.delete(0, END)
        for csv in self.csv_reports:
            self.csv_listbox.insert(END, csv)
        for pdf in self.pdf_reports:
            self.pdf_listbox.insert(END, pdf)
        for excel in self.excel_reports:
            self.excel_listbox.insert(END, excel)

    def return_press(self):
        self.viewer_f.pack_forget()
        self.step_two.pack(fill=tkinter.BOTH, pady=15, padx=5)
        self.pt2_label.lift()

    def reset_process(self):
        self.pdf_reports.clear()
        self.excel_reports.clear()
        self.csv_reports.clear()
        self.curr_data = [None, None, None]
