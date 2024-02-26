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

        exit_button = ttk.Button(self.window, text="X", command=self.window.destroy)

        minimise_button = ttk.Button(self.window, text="_", command=lambda: self.window.state(newstate='iconic'))
        maximise_button = ttk.Button(self.window, text="🗖", command=lambda: self.window.state(newstate='zoomed'))

        exit_button.pack(side='right', anchor=tk.NE)
        maximise_button.pack(side='right', anchor=tk.NE)
        minimise_button.pack(side='right', anchor=tk.NE)

    def make_ui_frame(self):
        pass

    def make_page_frame(self):
        pass


class Conductor(Context):
    def __init__(self, cid, pages):
        super().__init__(cid, pages)
        ui = self.make_ui_frame()
        ui.pack(side='left', anchor=tk.NW)
        self.window.mainloop()

    def make_ui_frame(self):
        ui_frame = ttk.Frame(self.window)

        label = ttk.Label(ui_frame, text='address bar', anchor=tk.E, background='#ccffff')
        address = tk.StringVar()
        address_bar = ttk.Entry(ui_frame, textvariable=address)

        # ToDo: fill in address loading
        go_to_button = ttk.Button(ui_frame, text='Go To', command=lambda: print('address: ', address.get()))
        # ToDo: fill in collaboration link generation
        collaboration_menu_button = ttk.Button(ui_frame, text='collaboration menu',
                                               command=lambda: self.start_collaboration())

        address_bar.grid(column=0, row=1, sticky=tk.NW)
        go_to_button.grid(column=1, row=1, sticky=tk.W)
        label.grid(column=0, row=2)
        collaboration_menu_button.grid(column=1, row=2)

        return ui_frame

    def start_collaboration(self):
        collab_menu = tk.Tk()
        collab_menu.geometry('300x100')
        collab_menu.title('collaboration for ' + self.cid)
        link = ttk.Label(collab_menu, text='gaudy://this_is_a_placeholder')
        collab_label = ttk.Label(collab_menu, text='link for collaboration')

        connect_link = tk.StringVar()
        enter_link = ttk.Entry(collab_menu, textvariable=connect_link)

        collab_button = ttk.Button(collab_menu, text='start collaborating',
                                   command=lambda: print("connecting to ", connect_link.get()))

        link.pack()
        collab_label.pack()
        enter_link.pack()
        collab_button.pack()


class Collaborator(Context):
    pass
