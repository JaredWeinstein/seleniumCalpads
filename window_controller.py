import tkinter.ttk as ttk
import time
from threading import Thread
from tkinter import *
from tkinter import filedialog
import browser_controller as bc
from tkinter import messagebox
import json
from ttkwidgets.autocomplete import AutocompleteCombobox

school = []
json_file_path = 'school_data.json'
with open(json_file_path, 'r') as j:
    school_data = json.loads(j.read())
for i in school_data.keys():
    school.append(i[-7:] + " - "+ school_data[i])

class WindowController:

    def __init__(self):

        def check(event):
            value = event.widget.get()
            if value == '':
                data = school[0:200]
            else:
                data = []
            counter = 0
            for item in school:
                if counter > 200:
                    break
                if value.lower() in item.lower():
                    data.append(item)
                    counter+=1
            update(data)


        def update(data):
            # Clear the Combobox
            self.l_list.delete(0, END)
            # Add values to the combobox
            for value in data:
                self.l_list.insert(END, value)

        window = Tk()
        window.geometry("550x400")
        window.title("CALPADS report fetcher")
        self.window = window

        self.menu = StringVar()
        self.n = StringVar()
        self.n.set('Please choose the year')
        self.menu.set("Select a Term")
        self.y_list = ttk.Combobox(self.window, textvariable=self.n)
        self.y_list['values'] = ["2022-2023", "2021-2022", "2020-2021", "2019-2020", "2018-2019", "2017-2018",
                                 "2016-2017",
                                 "2015-2016"]
        self.y_list.place(x=165, y=170)

        self.folder_path = StringVar()
        self.folder_button = Button(window, text="File selector", command=lambda : self.dir_searcher())
        self.folder_button.place(x=200, y=270)

        folder_label = Label(window, text="Select a folder for the downloads:")
        folder_label.place(x=10, y=265)
        self.current_location = Label(window, textvariable=self.folder_path)
        self.current_location.place(x=20,y=310)

        u_label = Label(window, text="Calpads Username:")
        u_label.place(x=20, y=20)

        p_label = Label(window, text="Calpads Password:")
        p_label.place(x=21, y=60)

        l_label = Label(window, text="Search for and select the \n LEA Code/School  from the list ")
        l_label.place(x=0, y=100)

        y_label = Label(window, text="Report year:")
        y_label.place(x=55, y=170)

        t_label = Label(window, text="Which report period?")
        t_label.place(x=10, y=210)

        self.u_box = Entry(window, width=30)
        self.u_box.place(x=165, y=20)

        self.p_box = Entry(window, show="*",width=30)
        self.p_box.place(x=165, y=60)

        self.l_box = Entry(window, width=35)
        self.l_box.bind('<KeyRelease>', check)
        self.l_box.place(x=165, y=100)
        self.l_list = Listbox(window, width=60)
        self.l_list.place(x=165,y=140)
        update(school)

        self.t_list = OptionMenu(window, self.menu, "Fall 1", "Fall 2", "EOY1", "EOY2", "EOY3", "EOY4")
        self.t_list.place(x=170, y=210)

        self.submit = Button(window, text="Submit", command=lambda : self.submit_press())
        self.submit.place(x=170, y=350)

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()

    def submit_press(self):
        if self.n.get() == 'Please choose the year' or self.menu.get() == "Select a Term" or self.u_box.get() == "" or self.p_box.get() == "" or self.l_list.get() == "":
            messagebox.showerror("Error", "Please input data for every field")
            return
        self.submit['state'] = DISABLED
        t1 = Thread(target=self.browser_create, daemon=True)
        t1.start()
        for widgets in self.window.winfo_children():
            widgets.place(anchor="nw", x=0, y=0, width=0, height=0)

    def dir_searcher(self):
        filename = filedialog.askdirectory()
        self.folder_path.set(filename)
        self.current_location['text'] = ("The current download location is: " + self.folder_path.__str__())

    def browser_create(self):
        browser = bc.BrowserController(self.u_box.get(), self.p_box.get(), self.l_list.get()[:7], self.menu.get(),self.n.get(),self.folder_path.get())
        browser.run_browser()

    def quit_program(self):
        self.window.quit()