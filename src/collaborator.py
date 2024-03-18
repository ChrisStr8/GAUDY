from context import Context

import dom

import socket
import select
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox

import styleDefaults

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
        self.conductor = socket.create_connection((host, port))
        self.conductor.setblocking(False)
        self.buffer = bytearray()
        self.current_page_data = None
        self.page = None

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
        ready = select.select([self.conductor], [], [], 0)

        if self.conductor in ready[0]:
            # Data is available
            while True:
                try:
                    # Receive data from Conductor
                    response = self.conductor.recv(4096, 0)
                except BlockingIOError:
                    # End of incoming data
                    break
                if len(response) == 0:
                    # Connection has been lost
                    messagebox.showinfo('Session Closed', 'Conductor has ended the session',)
                    exit()
                # Add data to buffer
                self.buffer.extend(response)

        # Look for messages in buffer
        # Messages are serialised HTML data terminated by a form-feed
        while b'\f' in self.buffer:
            idx = self.buffer.find(b'\f')
            page_data = self.buffer[0:idx]
            self.buffer = bytearray(self.buffer[idx+1:])
            # Message received, load the page
            self.visit_page(page_data)

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

        # Layout Address Field
        ui_frame.grid_columnconfigure(0, weight=1)
        address_bar.grid(row=0, column=0, sticky=tk.NSEW)
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
            # Destroy current page
            if self.current_page() is not None:
                self.current_page().delete()

            # Setup page frame
            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)

            # Create page from serialised data
            self.page = dom.deserialise_page(page_data, page_frame)
            self.current_page_data = page_data

            # Set window title, address, and layout labels.
            self.window.title(self.current_page().title)
            self.set_address(self.current_page().address)
            self.set_label_length()
        except ValueError as e:
            print(e)


if __name__ == '__main__':
    Collaborator('Collaborator', 'localhost', 10000)
