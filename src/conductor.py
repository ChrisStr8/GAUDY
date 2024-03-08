from context import Context
import serialiser
import dom

import socket
import select

import tkinter as tk
import tkinter.ttk as ttk

HOMEPAGE = 'http://127.0.0.1:8000/testPage.html'

class Conductor(Context):
    def __init__(self, cid):
        super().__init__(cid)
        self.address_bar = None
        ui = self.make_ui_frame()
        self.pages = [None]
        self.page_history = list()
        self.back_history = list()
        self.collaborators = list()
        self.current_page_data = None
        self.go_to_page(HOMEPAGE)

        self.server_socket = socket.create_server(('0.0.0.0', 10000))
        self.window.after(10, lambda: self.check_network())

        self.window.mainloop()

    def set_address(self, address):
        self.address_bar.delete(0, tk.END)
        self.address_bar.insert(0, address)

    def check_network(self):
        ready = select.select([self.server_socket], [], [], 0)

        if self.server_socket in ready[0]:
            connection, address = self.server_socket.accept()
            self.collaborators.append(connection)
            connection.sendall(self.current_page_data)
            connection.sendall(b'\f')

        self.window.after(1000, lambda: self.check_network())

    def current_page(self):
        return self.pages[self.focused_page]

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
        address.set(HOMEPAGE)
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
        self.address_bar = address_bar

        return ui_frame

    def go(self, url):
        self.page_history.append((self.current_page().address, self.current_page_data))
        self.go_to_page(url)

    def finish_going(self):
        self.window.title(self.current_page().title)
        for anchor in self.current_page().find_nodes('a'):
            children = list()
            anchor.find_nodes(children, 'data')
            for child in children:
                (lambda c=child: c.tk_object.bind("<Button-1>", lambda event: self.go(c.parent.get_attr('href'))))()
        self.set_label_length()

        for collaborator in self.collaborators:
            try:
                collaborator.sendall(self.current_page_data)
                collaborator.sendall(b'\f')
            except IOError:
                collaborator.close()
                self.collaborators.remove(collaborator)

    def go_to_page(self, url):
        self.back_history = list()
        self.set_address(url)

        try:
            if self.current_page() is not None:
                self.current_page().delete()

            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)
            self.pages[self.focused_page] = dom.create_page_from_url(url, page_frame)
            self.current_page_data = serialiser.bytes_from_html(self.current_page())
            self.finish_going()

        except ValueError as e:
            print(e)

    def revisit(self, page_data):
        self.set_address(page_data[0])
        try:
            self.current_page().delete()

            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)
            self.pages[self.focused_page] = dom.deserialise_page(page_data[1], page_frame)
            self.current_page_data = page_data[1]
            self.finish_going()

        except ValueError as e:
            print(e)

    def back(self):
        if len(self.page_history) > 0:
            prev = self.page_history.pop()
            self.back_history.append((self.current_page().address, self.current_page_data))
            self.revisit(prev)

    def forward(self):
        if len(self.back_history) > 0:
            prev = self.back_history.pop()
            self.page_history.append((self.current_page().address, self.current_page_data))
            self.revisit(prev)

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
