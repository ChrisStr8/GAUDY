from context import Context

import dom

import socket
import select
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import re

from messageProtocol import MessageProtocol
from messageType import *


def disconnect():
    messagebox.showinfo('Session Closed', 'Conductor has disconnected.')
    exit()


class Collaborator(Context):
    """
    Collaborator class connects to a Conductor and displays the same content as the Conductor.
    """

    def __init__(self, cid, host, port):
        """
        Create a new collaborator connected to the given Conductor.
        Conductor periodically checks for messages from the Conductor and responds appropriately .
        :param cid: The Context Name
        :param host: The remote server to connect to (ip / dns name)
        :param port: The port to connect on
        """
        # styleDefaults.dark_mode = True
        # Call Context initialiser to create window.
        super().__init__(cid)

        # Setup user interface
        self.address_bar = None
        ui = self.make_ui_frame()

        # Connect to Conductor
        self.connection = socket.create_connection((host, port))
        self.connection.setblocking(False)
        self.conductor = MessageProtocol(self.connection, self.cid)
        self.current_page_data = None

        # Setup network check.
        self.window.after(10, lambda: self.check_network())

        # Start the application!
        self.window.mainloop()

    def check_network(self):
        """
        Check for messages from the Conductor and process them.
        This is currently limited to sending page data.
        """

        # Check for incoming data from the conductor.
        ready = select.select([self.connection], [], [], 0)

        if self.connection in ready[0]:
            messages = self.conductor.receive()
            for m in messages:
                if m.message_type == MESSAGE_DISCONNECTED:
                    disconnect()
                if m.message_type == MESSAGE_INVALID:
                    disconnect()
                elif m.message_type == MESSAGE_TIMEOUT:
                    disconnect()
                elif m.message_type == MESSAGE_NAVIGATION:
                    self.set_address(m.data.decode('utf-8'))
                elif m.message_type == MESSAGE_PAGEDATA:
                    self.visit_page(m.data)
                else:
                    disconnect()

        # Schedule next network check one second later
        self.window.after(1000, lambda: self.check_network())

    def make_ui_frame(self):
        """
        Setup User Interface for the Collaborator.
        Collaborator User Interface is only an address field.
        """

        # Create Frame to contain UI
        ui_frame = ttk.Frame(self.root)
        ui_frame.grid(column=0, row=0, sticky=tk.EW)

        # Create Address Field
        address = tk.StringVar()
        address.set("")
        address_bar = ttk.Entry(ui_frame, textvariable=address)

        # Create Navigation Buttons (back and forward)
        nav_section = ttk.Frame(ui_frame)
        ttk.Button(nav_section, text='Back', style='Gaudy.TButton', command=self.back).grid(column=0, row=1,
                                                                                            sticky=tk.W)
        ttk.Button(nav_section, text='Forward', style='Gaudy.TButton', command=self.forward).grid(column=1, row=1,
                                                                                                  sticky=tk.E)

        # create go button
        go_to_button = ttk.Button(ui_frame, text='Go!', command=lambda: self.go(address.get()),
                                  style='GaudyGo.TButton')

        # Layout Address Field
        ui_frame.grid_columnconfigure(1, weight=1)
        nav_section.grid(row=0, column=0, sticky=tk.W)
        address_bar.grid(row=0, column=1, sticky=tk.NSEW)
        go_to_button.grid(row=0, column=2, sticky=tk.E)
        self.address_bar = address_bar

        return ui_frame

    def current_page(self):
        """
        Get the currently displayed page.
        :return: The current page.
        """
        return self.page

    def visit_page(self, page_data):
        """
        Load a page from serialised data.
        Uses the dom and serialiser modules.
        :param page_data: Serialised page data
        """
        try:

            # Setup page frame
            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)

            # Create page from serialised data
            self.page = dom.deserialise_page(page_data, page_frame)
            self.current_page_data = page_data

            # Set window title, address, and layout labels.
            self.window.title(self.current_page().title)
            self.set_address(self.current_page().address)

            self.page.render()
            self.page.renderer.bind_links(self)
        except ValueError as e:
            print(e)

    def go(self, url):
        print(url)
        self.conductor.navigate(url)

    def back(self):
        self.conductor.back()

    def forward(self):
        self.conductor.forward()


if __name__ == '__main__':
    Collaborator('Collaborator', 'localhost', 10000)
