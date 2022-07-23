import tkinter.ttk as ttk
import time
from threading import Thread
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import browser_controller
import browser_controller as bc


class WindowController:
    def __init__(self):

        window = Tk()
        window.geometry("400x350")
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
        self.y_list.place(x=150, y=140)

        self.folder_path = StringVar()
        self.folder_button = Button(window, text="File selector", command=lambda : self.dir_searcher())
        self.folder_button.place(x=200, y=230)

        folder_label = Label(window, text="Select a folder for the downloads:")
        folder_label.place(x=20, y=230)
        self.current_location = Label(window, textvariable=self.folder_path)
        self.current_location.place(x=20,y=270)

        u_label = Label(window, text="Calpads Username:")
        u_label.place(x=20, y=20)

        p_label = Label(window, text="Calpads Password:")
        p_label.place(x=21, y=60)

        l_label = Label(window, text="LEA School Code:")
        l_label.place(x=24, y=100)
        explain = Label(window, text="(7 digit code)")
        explain.place(x=32, y=115)

        y_label = Label(window, text="Report year:")
        y_label.place(x=55, y=150)

        t_label = Label(window, text="Which report period?")
        t_label.place(x=10, y=190)

        self.u_box = Entry(window, width=30)
        self.u_box.place(x=150, y=20)

        self.p_box = Entry(window, show="*",width=30)
        self.p_box.place(x=150, y=60)

        self.l_box = Entry(window)
        self.l_box.place(x=150, y=100)

        self.t_list = OptionMenu(window, self.menu, "Fall 1", "Fall 2", "EOY1", "EOY2", "EOY3", "EOY4")
        self.t_list.place(x=150, y=180)

        self.submit = Button(window, text="Submit", command=lambda : self.submit_press())
        self.submit.place(x=170, y=320)

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()

    def submit_press(self):
        if self.n.get() == 'Please choose the year' or self.menu.get() == "Select a Term" or self.u_box.get() == "" or self.p_box.get() == "" or self.l_box.get() == "":
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

    def message(self):
        pass

    def browser_create(self):
        browser = bc.BrowserController(self.u_box.get(), self.p_box.get(), self.l_box.get(), self.menu.get(),self.n.get(),self.folder_path.get())
        browser.run_browser()


