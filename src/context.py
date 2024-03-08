import select
import socket
import tkinter as tk
import tkinter.ttk as ttk

import dom
import serialiser
from styleDefaults import StyleDefaults

import sys as sys


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
        style.configure('Gaudy.TFrame', background=StyleDefaults.backgroundColour)
        style.configure('Gaudy.TButton', background=StyleDefaults.backgroundColour,
                        foreground=StyleDefaults.secondaryColour, font=('Sans', 12, 'bold'))
        style.configure('GaudyGo.TButton', background=StyleDefaults.primaryColour,
                        foreground=StyleDefaults.backgroundColour, font=('Sans', 12, 'bold'))

        # element styles
        style.configure('div.TLabel', font=(StyleDefaults.primaryFont, StyleDefaults.defaultFontSize),
                        foreground=StyleDefaults.defaultColour,
                        background=StyleDefaults.backgroundColour)

        style.configure('h1.TLabel', font=(StyleDefaults.headingFont, StyleDefaults.h1FontSize),
                        foreground=StyleDefaults.h1Colour,
                        background=StyleDefaults.backgroundColour)
        style.configure('h2.TLabel', font=(StyleDefaults.headingFont, StyleDefaults.h2FontSize),
                        foreground=StyleDefaults.h2Colour,
                        background=StyleDefaults.backgroundColour)
        style.configure('h3.TLabel', font=(StyleDefaults.headingFont, StyleDefaults.h3FontSize),
                        foreground=StyleDefaults.h3Colour,
                        background=StyleDefaults.backgroundColour)
        style.configure('h4.TLabel', font=(StyleDefaults.headingFont, StyleDefaults.h4FontSize),
                        foreground=StyleDefaults.h4Colour,
                        background=StyleDefaults.backgroundColour)
        style.configure('h5.TLabel', font=(StyleDefaults.headingFont, StyleDefaults.h5FontSize),
                        foreground=StyleDefaults.h5Colour,
                        background=StyleDefaults.backgroundColour)
        style.configure('h6.TLabel', font=(StyleDefaults.headingFont, StyleDefaults.h6FontSize),
                        foreground=StyleDefaults.h6Colour,
                        background=StyleDefaults.backgroundColour)

        style.configure('p.TLabel', font=(StyleDefaults.primaryFont, StyleDefaults.defaultFontSize),
                        foreground=StyleDefaults.primaryColour,
                        background=StyleDefaults.backgroundColour)
        style.configure('hr.TLabel', font=(StyleDefaults.primaryFont, StyleDefaults.defaultFontSize),
                        foreground=StyleDefaults.primaryColour,
                        background=StyleDefaults.backgroundColour)
        style.configure('br.TLabel', font=(StyleDefaults.primaryFont, StyleDefaults.defaultFontSize),
                        background=StyleDefaults.backgroundColour)
        style.configure('span.TLabel', font=(StyleDefaults.primaryFont, StyleDefaults.importantFontSize),
                        foreground='#39FF14',
                        background=StyleDefaults.backgroundColour)
        style.configure('a.TLabel', font=(StyleDefaults.primaryFont, StyleDefaults.defaultFontSize, 'underline'),
                        foreground=StyleDefaults.primaryColour,
                        background=StyleDefaults.backgroundColour)

        self.root = ttk.Frame(self.window, style='Gaudy.TFrame')
        self.root.grid(row=0, column=0, sticky=tk.NSEW)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.window.title(cid)
        self.window.grid()
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.bind("<Configure>", lambda x: self.set_label_length())

    def make_ui_frame(self):
        pass

    def current_page(self):
        return None

    def set_label_length(self):
        if self.current_page() is None:
            return
        width = self.root.winfo_width() - self.current_page().scrollbar.winfo_width()
        for data in self.current_page().find_nodes('data'):
            if data.tk_object is not None:
                data.tk_object.configure(wraplength=width)