import tkinter as tk
import tkinter.ttk as ttk

import dom

homepage = 'https://info.cern.ch/hypertext/WWW/TheProject.html'


# when changing page remember to delete the old one
class Context:
    cid = None
    pages = None
    window = None
    root = None
    focused_page = 0

    def __init__(self, cid):
        self.cid = cid

        self.window = tk.Tk()

        # Configure Style
        style = ttk.Style()
        style.configure('Gaudy.TFrame', background='#ccccff')
        style.configure('Gaudy.TButton', background='#800080', foreground='#39FF14', font=('Sans', '12', 'bold'))
        style.configure('GaudyGo.TButton', background='#39ff14', foreground='#0000FF', font=('Sans', '12', 'bold'))
        self.root = ttk.Frame(self.window, style='Gaudy.TFrame')
        self.root.grid(row=0, column=0, sticky=tk.NSEW)
        self.root.grid_columnconfigure(0, weight=1)
        self.window.title(cid)
        self.window.grid()
        self.window.grid_columnconfigure(0, weight=1)

    def make_ui_frame(self):
        pass

    def make_page_frame(self):
        pass


class Conductor(Context):

    def __init__(self, cid, pages):
        super().__init__(cid)
        ui = self.make_ui_frame()
        self.pages = pages
        self.page_history = list()
        self.back_history = list()
        self.go_to_page(homepage)
        self.window.mainloop()


    def make_ui_frame(self):
        ui_frame = ttk.Frame(self.root)
        ui_frame.grid(column=0, row=0, sticky=tk.EW)

        # TODO: Make these actually navigate
        # TODO: Icons for nav buttons
        nav_section = ttk.Frame(ui_frame)
        ttk.Button(nav_section, text='Back', style='Gaudy.TButton', command=self.back).grid(column=0, row=1,
                                                                                            sticky=tk.W)
        ttk.Button(nav_section, text='Forward', style='Gaudy.TButton', command=self.forward).grid(column=1, row=1,
                                                                                                  sticky=tk.E)

        address = tk.StringVar()
        address_bar = ttk.Entry(ui_frame, textvariable=address)

        # ToDo: fill in address loading
        go_to_button = ttk.Button(ui_frame, text='Go!', command=lambda: self.go(address.get()),
                                  style='GaudyGo.TButton')
        # ToDo: fill in collaboration link generation
        collaborate_button = ttk.Button(ui_frame, text='Collaborate',
                                        command=lambda: self.display_collaboration_options(), style='Gaudy.TButton')

        ui_frame.grid_columnconfigure(1, weight=1)
        nav_section.grid(row=0, column=0, sticky=tk.W)
        address_bar.grid(row=0, column=1, sticky=tk.NSEW)
        go_to_button.grid(row=0, column=2, sticky=tk.E)
        collaborate_button.grid(row=0, column=3, sticky=tk.E)
        address_bar.bind('<Return>', lambda e: go_to_button.invoke())
        self.window.bind('<Control-l>', lambda e: address_bar.focus())

        address_bar.focus()

        return ui_frame

    def go(self, url):
        self.page_history.append(self.pages[self.focused_page].address)
        self.go_to_page(url)

    def go_to_page(self, url):
        print(url)
        try:
            if self.pages[self.focused_page] is not None:
                self.pages[self.focused_page].delete()

            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0)
            self.pages[self.focused_page] = dom.HtmlPage(url, page_frame)

        except ValueError:
            print('invalid url')

    def back(self):
        # print(self.page_history)
        if len(self.page_history) > 0:
            url = self.page_history.pop()
            self.back_history.append(self.pages[self.focused_page].address)
            self.go_to_page(url)
            # print(self.back_history)

    def forward(self):
        print(self.back_history)
        if len(self.back_history) > 0:
            url = self.back_history.pop()
            self.go(url)

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


if __name__ == '__main__':
    c1 = Conductor('context1', [])
