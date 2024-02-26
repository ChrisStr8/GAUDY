import tkinter as tk
import tkinter.ttk as ttk

import dom


# when changing page remember to delete the old one
class Context:
    cid = None
    pages = []
    window = tk.Tk()
    window.geometry('500x200')
    window.tk_setPalette(background="#ccccff")

    def __init__(self, cid, pages):
        self.cid = cid
        self.pages = pages
        self.window.title(cid)

    def make_ui_frame(self):
        pass

    def make_page_frame(self):
        pass


class Conductor(Context):
    def __init__(self, cid, pages):
        super().__init__(cid, pages)
        ui = self.make_ui_frame()
        ui.pack(side='left', anchor=tk.NW)
        self.display_pages()
        self.window.mainloop()

    def make_ui_frame(self):
        ui_frame = ttk.Frame(self.window)

        label = ttk.Label(ui_frame, text='address bar', anchor=tk.E, background='#ccffff')
        address = tk.StringVar()
        address_bar = ttk.Entry(ui_frame, textvariable=address)

        # ToDo: fill in address loading
        go_to_button = ttk.Button(ui_frame, text='Go To', command=lambda: self.go_to_page(address.get()))
        # ToDo: fill in collaboration link generation
        collaboration_menu_button = ttk.Button(ui_frame, text='collaboration menu',
                                               command=lambda: self.display_collaboration_options())

        address_bar.grid(column=0, row=1, sticky=tk.NW)
        go_to_button.grid(column=1, row=1, sticky=tk.W)
        label.grid(column=0, row=2)
        collaboration_menu_button.grid(column=1, row=2)

        return ui_frame

    def go_to_page(self, url):
        print(url)
        try:
            self.pages[0] = dom.HtmlPage(url)
        except ValueError:
            print('invalid url')

    def display_pages(self):
        for page in self.pages:
            page.add_tk(self.window).pack()

    def display_collaboration_options(self):
        collab_menu = tk.Tk()
        collab_menu.geometry('300x100')
        collab_menu.title('collaboration for ' + self.cid)
        link = tk.Text(collab_menu, height=1)
        link.insert('1.0', 'gaudy://this_is_a_placeholder')
        link['state'] = 'disabled'
        collab_label = ttk.Label(collab_menu, text='link for collaboration')

        connect_link = tk.StringVar()
        enter_link = ttk.Entry(collab_menu, textvariable=connect_link)

        collab_button = ttk.Button(collab_menu, text='start collaborating',
                                   command=lambda: print("connecting to ", connect_link.get()))

        link.pack()
        collab_label.pack()
        enter_link.pack()
        collab_button.pack()
        collab_menu.mainloop()


class Collaborator(Context):
    pass
