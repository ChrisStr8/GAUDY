import tkinter as tk
import tkinter.ttk as ttk


# when changing page remember to delete the old one
class Context:
    def __init__(self, cid, pages):
        self.cid = cid
        self.pages = pages

        self.window = tk.Tk()
        self.window.title(cid)
        self.window.geometry('500x200')
        self.window.tk_setPalette(background="#ccccff")

    def make_ui_frame(self):
        pass

    def make_page_frame(self):
        pass


class Conductor(Context):
    def __init__(self, cid, pages):
        super().__init__(cid, pages)
        ui = self.make_ui_frame()
        ui.grid()
        self.window.mainloop()

    def make_ui_frame(self):
        ui_frame = ttk.Frame(self.window)
        label0 = ttk.Label(ui_frame, text='UI element0', anchor=tk.E, background='#ccffff')
        label1 = ttk.Label(ui_frame, text='UI element1', anchor=tk.E, background='#ccffff')
        label0.grid(column=0, row=0, sticky=tk.W)
        label1.grid(column=1, row=0, sticky=tk.W)
        return ui_frame


class Collaborator(Context):
    pass


class Ui(ttk.Frame):
    def __init__(self, window):
        super().__init__()
        label = ttk.Label(self, text='add UI here')
        self.url = (tk.StringVar())
        # self.url.set('url')
        urlbox = ttk.Entry(self, textvariable=self.url)

        urlbox.pack()
        label.pack()
