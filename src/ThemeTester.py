import tkinter as tk
import tkinter.ttk as ttk


class Colour:

    def __init__(self, frame, update):
        self.brightnesses = [
            ('Bright', 'ff', '22'),
            ('Deep', 'aa', '22'),
            ('Dull', 'bb', '44'),
            ('Pale', 'ff', '77'),
            ('Dark', '77', '22')]
        self.colours = [
            ('Red', 'hll'),
            ('Green', 'lhl'),
            ('Blue', 'llh'),
            ('Yellow', 'hhl'),
            ('Magenta', 'hlh'),
            ('Cyan', 'lhh')]

        self.brightness = tk.IntVar(value=0)
        self.shade = tk.IntVar(value=0)

        for i in range(len(self.brightnesses)):
            name = self.brightnesses[i][0]
            ttk.Radiobutton(frame, text=name, variable=self.brightness, value=i, command=update).grid(column=0, row=i)

        for i in range(len(self.colours)):
            name = self.colours[i][0]
            ttk.Radiobutton(frame, text=name, variable=self.shade, value=i, command=update).grid(column=1, row=i)

    def __str__(self):
        return self.brightnesses[self.brightness.get()][0] + ' ' + self.colours[self.shade.get()][0]

    def colour_value(self):
        b = self.brightnesses[self.brightness.get()]
        s = self.colours[self.shade.get()]
        h = b[1]
        l = b[2]

        colour ='#' + s[1].replace('l', l).replace('h', h)
        print(colour)

        return colour


def colour_tester():
    window = tk.Tk()
    window.title("Theme Tester")

    window.grid()
    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    frame = ttk.Frame(window)
    frame.grid(sticky=tk.NSEW)

    label_value = tk.StringVar()
    style = ttk.Style()
    reconfigure = lambda: style.configure('test.TLabel', foreground=foreground.colour_value(),
                                          background=background.colour_value(), font=('Liberation Sans', 12))

    ttk.Label(frame, text="Foreground").grid(column=0, row=0)
    fg_frame = ttk.Frame(frame, relief='groove', padding=5)
    foreground = Colour(fg_frame, lambda: label_value.set(str(foreground)))
    fg_frame.grid(column=0, row=1)

    ttk.Label(frame, text="Background").grid(column=1, row=0)
    bg_frame = ttk.Frame(frame, relief='groove', padding=5)
    background = Colour(bg_frame, reconfigure)
    bg_frame.grid(column=1, row=1)

    reconfigure()
    label_value.set(str(foreground))

    test_frame = ttk.Frame(frame)
    test_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)
    test_text = ttk.Label(test_frame, textvariable=label_value, style='test.TLabel')
    test_text.grid(sticky=tk.NSEW)

    window.mainloop()


if __name__ == '__main__':
    colour_tester()
