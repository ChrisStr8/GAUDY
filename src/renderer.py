import tkinter as tk
import tkinter.ttk as ttk

from styleDefaults import StyleDefaults


class Renderer:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=600, height=400, bg=StyleDefaults.backgroundColour)
        self.line_num = 0
        self.xlocation = 0
        self.ylocation = 0

    def render(self, root):
        self.canvas.delete('all')
        self.line_num = 0
        self.xlocation = 0
        self.ylocation = 0
        self.render_node(root, [])

    def render_node(self, node, styling):
        for child in node.children:
            # print(child.tag)
            if child.tag == 'data':
                top_spacing = 1
                bottom_spacing = 1
                start_spacing = 5
                end_spacing = 1

                font = StyleDefaults.primaryFont
                font_size = StyleDefaults.defaultFontSize
                font_colour = StyleDefaults.defaultColour

                # print(child.get_attr("text"))
                text = self.canvas.create_text(
                    (self.xlocation + start_spacing, self.ylocation + top_spacing),
                    anchor=tk.NW,
                    text=child.get_attr("text"),
                    fill=font_colour,
                    font=font + " " + str(font_size)
                )
                # move to new line
                self.ylocation += font_size + top_spacing + bottom_spacing
                self.xlocation = 0
                # print(text)

            self.render_node(child, styling)
