from context import Context

import dom

import socket
import select
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox


class Collaborator(Context):
    def __init__(self, cid, host, port):
        super().__init__(cid)
        self.address_bar = None
        ui = self.make_ui_frame()
        self.conductor = socket.create_connection((host, port))
        self.buffer = bytearray()
        self.current_page_data = None
        self.page = None

        self.window.after(10, lambda: self.check_network())

        self.window.mainloop()

    def check_network(self):
        ready = select.select([self.conductor], [], [], 0)

        if self.conductor in ready[0]:
            while True:
                try:
                    response = self.conductor.recv(4096, socket.MSG_DONTWAIT)
                except BlockingIOError:
                    break
                if len(response) == 0:
                    messagebox.showinfo('Session Closed', 'Conductor has ended the session',)
                    exit()
                self.buffer.extend(response)

        while b'\f' in self.buffer:
            idx = self.buffer.find(b'\f')
            page_data = self.buffer[0:idx]
            self.buffer = bytearray(self.buffer[idx+1:])
            self.visit_page(page_data)

        self.window.after(1000, lambda: self.check_network())

    def make_ui_frame(self):
        ui_frame = ttk.Frame(self.root)
        ui_frame.grid(column=0, row=0, sticky=tk.EW)

        address = tk.StringVar()
        address.set("")
        address_bar = ttk.Entry(ui_frame, textvariable=address)

        ui_frame.grid_columnconfigure(0, weight=1)
        address_bar.grid(row=0, column=0, sticky=tk.NSEW)

        address_bar.focus()
        self.address_bar = address_bar

        return ui_frame

    def set_address(self, address):
        self.address_bar.delete(0, tk.END)
        self.address_bar.insert(0, address)

    def current_page(self):
        return self.page

    def visit_page(self, page_data):
        try:
            if self.current_page() is not None:
                self.current_page().delete()

            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)
            self.page = dom.deserialise_page(page_data, page_frame)
            self.current_page_data = page_data

            self.window.title(self.current_page().title)
            self.set_address(self.current_page().address)
            self.set_label_length()

        except ValueError as e:
            print(e)


if __name__ == '__main__':
    Collaborator('Collaborator', 'localhost', 10000)
