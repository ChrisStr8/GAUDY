import tkinter as tk
import tkinter.ttk as ttk


class Context:
    def __init__(self, id, pages):
        self.id = id
        self.pages = pages

        self.window = tk.Tk()
        frame = ttk.Frame(self.window)
        greeting = tk.Label(
            text="Hello, Tkinter",
            width=25,
            height=10,
            bg="#ccccff"
        )
        greeting.pack()
        self.window.mainloop()


class Conductor(Context):
    pass


class Collaborator(Context):
    pass
