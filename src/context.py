import re
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font

from styleDefaults import StyleDefaults


class Context:
    """
    Context is the base class for Conductor and Collaborator.
    Manages top-level TK window state and has some shared utility functions.
    """

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
        style.theme_use('clam')
        style.configure('Gaudy.TFrame', background=StyleDefaults.backgroundColour)
        style.configure('Gaudy.TButton', background=StyleDefaults.backgroundColour,
                        foreground=StyleDefaults.secondaryColour, font=(StyleDefaults.userInterfaceFont, 10, 'bold'))
        style.map('Gaudy.TButton',
                  background=[('active', StyleDefaults.button_active), ('!disabled', StyleDefaults.button_inactive)],
                  foreground=[('active', StyleDefaults.button_text_active),
                              ('!disabled', StyleDefaults.button_text_inactive)])

        style.configure('GaudyGo.TButton', background=StyleDefaults.primaryColour,
                        foreground=StyleDefaults.deep_green, font=(StyleDefaults.userInterfaceFont, 10, 'bold'))
        style.map('GaudyGo.TButton',
                  background=[('active', StyleDefaults.go_button_active),
                              ('!disabled', StyleDefaults.go_button_inactive)],
                  foreground=[('active', StyleDefaults.go_button_text_active),
                              ('!disabled', StyleDefaults.go_button_text_inactive)])

        # Layout top-level window
        self.root = ttk.Frame(self.window, style='Gaudy.TFrame')
        self.root.grid(row=0, column=0, sticky=tk.NSEW)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.window.title(cid)
        self.window.grid()
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)


    def make_ui_frame(self):
        pass

    def current_page(self):
        return None

    def set_address(self, address):
        """
        Change the value shown in the address bar.
        :param address: The address to show.
        """
        self.address_bar.delete(0, tk.END)
        self.address_bar.insert(0, address)


def set_wraplength(widget, width):
    if isinstance(widget, ttk.Label):
        widget.configure(wraplength=width)
    for child in widget.winfo_children():
        set_wraplength(child, width)
