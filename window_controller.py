import tkinter.ttk as ttk
from threading import Thread
from tkinter import *
from tkinter import filedialog
import browser_controller as bc
from tkinter import messagebox
import json

school = []
json_file_path = 'school_data.json'
with open(json_file_path, 'r') as j:
    school_data = json.loads(j.read())
for i in school_data.keys():
    school.append(i[-7:] + " - " + school_data[i])


class WindowController:

    def __init__(self):
        def check(event):
            value = event.widget.get()
            if value == '':
                data = school[0:100]
            else:
                data = []
            counter = 0
            for item in school:
                if counter > 100:
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

        window = Tk()
        window.geometry("500x550")
        window.title("CALPADS report fetcher")
        self.window = window

        u_label = Label(window, text="Calpads Username:")
        u_label.place(x=20, y=20)
        self.u_box = Entry(window, width=35)
        self.u_box.place(x=180, y=20)

        p_label = Label(window, text="Calpads Password:")
        p_label.place(x=21, y=60)
        self.p_box = Entry(window, show="*", width=35)
        self.p_box.place(x=180, y=60)

        l_label = Label(window, text="Search for and select the \n LEA Code/School  from the list:")
        l_label.place(x=0, y=100)
        self.l_box = Entry(window, width=40)
        self.l_box.bind('<KeyRelease>', check)
        self.l_box.place(x=180, y=100)
        self.l_list = Listbox(window, width=50, selectmode=SINGLE)
        self.l_list.configure(exportselection=False)
        self.l_list.place(x=200, y=140)
        update(school)

        y_label = Label(window, text="Report year:")
        y_label.place(x=90, y=320)
        self.year = StringVar()
        self.year.set('Please choose the year')
        y_list = ttk.Combobox(self.window, textvariable=self.year)
        y_list['values'] = ["2022-2023", "2021-2022", "2020-2021", "2019-2020", "2018-2019", "2017-2018", "2016-2017",
                            "2015-2016"]
        y_list.place(x=200, y=320)

        t_label = Label(window, text="Which report period?")
        t_label.place(x=55, y=360)
        self.term = StringVar()
        self.term.set("Select a Term")
        self.t_list = OptionMenu(window, self.term, "FALL1", "FALL2", "EOY1", "EOY2", "EOY3", "EOY4")
        self.t_list.place(x=200, y=350)

        file_type_label = Label(window, text="Choose what type of \n file to be exported:")
        file_type_label.place(x=50, y=400)
        self.file_type = StringVar()
        self.file_type.set("Select file type")
        file_type_list = OptionMenu(window, self.file_type, 'PDF', 'EXCEL', 'CSV')
        file_type_list.place(x=200, y=400)

        self.folder_path = StringVar()
        self.folder_button = Button(window, text="File selector", command=lambda: self.dir_searcher())
        self.folder_button.place(x=200, y=450)
        folder_label = Label(window, text="Select a folder for the downloads:")
        folder_label.place(x=10, y=450)
        self.current_location = Label(window, textvariable=self.folder_path)
        self.current_location.place(x=5, y=480)

        self.submit = Button(window, text="Submit", command=lambda: self.submit_press())
        self.submit.place(x=200, y=510)

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                window.destroy()
                self.browser.close_browser()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()

    def submit_press(self):
        if self.year.get() == 'Please choose the year' or self.term.get() == "Select a Term" or self.u_box.get() == "" \
                or self.p_box.get() == "" or self.l_list.curselection() == "":
            messagebox.showerror("Error", "Please input data for every field")
            return
        self.submit['state'] = DISABLED
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()

    def dir_searcher(self):
        filename = filedialog.askdirectory()
        self.folder_path.set(filename)
        self.current_location['text'] = ("The current download location is: " + self.folder_path.__str__())

    def browser_create(self):
        self.browser = bc.BrowserController(self.u_box.get(), self.p_box.get(),
                                       self.l_list.get(self.l_list.curselection())[:7],
                                       self.term.get(), self.year.get(), self.folder_path.get(), self.file_type.get())
        self.browser.run_browser()

    def quit_program(self):
        self.window.quit()
