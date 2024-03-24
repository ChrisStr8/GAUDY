import copy
import tkinter as tk
import tkinter.ttk as ttk

from styleDefaults import StyleDefaults


class Renderer:
    def __init__(self, parent, width, height):
        self.canvas = tk.Canvas(parent, width=width, height=height, bg=StyleDefaults.backgroundColour)
        self.x_location = 0
        self.y_location = 0
        self.x_next = 0
        self.y_next = 0
        self.line_number = 0
        self.line = []
        self.lines = []

    def render(self, root):
        self.canvas.delete('all')
        self.x_location = 0
        self.y_location = 0
        self.render_node(root, {})

    def render_node(self, node, styling):
        new_styling = copy.deepcopy(styling)
        elements = tuple()
        # load default style
        top_spacing = StyleDefaults.top_spacing
        bottom_spacing = StyleDefaults.bottom_spacing
        start_spacing = StyleDefaults.start_spacing
        end_spacing = StyleDefaults.end_spacing

        font = (StyleDefaults.primaryFont,)
        size = StyleDefaults.defaultFontSize
        foreground = StyleDefaults.defaultColour
        background = StyleDefaults.backgroundColour
        underline = False
        bold = False
        italic = False

        if node.tag == 'head':
            pass
        elif node.tag == 'title':
            return tuple()
        elif node.tag == 'body':
            pass
        elif node.tag == 'div':
            self.new_line(top_spacing + bottom_spacing)
            new_styling['font'] = StyleDefaults.userInterfaceFont
            new_styling['foreground'] = StyleDefaults.primaryColour
        elif node.tag == 'span':
            new_styling['italic'] = True
        elif node.tag == 'a':
            new_styling['foreground'] = StyleDefaults.link_colour
            new_styling['underline'] = True
        elif node.tag == 'table':
            self.new_line(top_spacing + bottom_spacing)
        elif node.tag == 'p':
            self.new_line(top_spacing + bottom_spacing)
        elif node.tag == 'pre':
            new_styling['font'] = StyleDefaults.monospaceFont
        elif (node.tag == 'h1' or node.tag == 'h2' or node.tag == 'h3' or node.tag == 'h4' or node.tag == 'h5'
              or node.tag == 'h6'):
            self.new_line(top_spacing + bottom_spacing)
            new_styling['font'] = StyleDefaults.headingFont
            if node.tag[1] == str(1):
                new_styling['size'] = StyleDefaults.h1FontSize
                new_styling['foreground'] = StyleDefaults.h1Colour
            elif node.tag[1] == str(2):
                new_styling['size'] = StyleDefaults.h2FontSize
                new_styling['foreground'] = StyleDefaults.h2Colour
            elif node.tag[1] == str(3):
                new_styling['size'] = StyleDefaults.h3FontSize
                new_styling['foreground'] = StyleDefaults.h3Colour
            elif node.tag[1] == str(4):
                new_styling['size'] = StyleDefaults.h4FontSize
                new_styling['foreground'] = StyleDefaults.h4Colour
            elif node.tag[1] == str(5):
                new_styling['size'] = StyleDefaults.h5FontSize
                new_styling['foreground'] = StyleDefaults.h5Colour
            elif node.tag[1] == str(6):
                new_styling['size'] = StyleDefaults.h6FontSize
                new_styling['foreground'] = StyleDefaults.h6Colour
        elif node.tag == 'hr':
            self.new_line(top_spacing + bottom_spacing)
        elif node.tag == 'br':
            pass
        elif node.tag == 'ul':
            self.new_line(top_spacing + bottom_spacing)
            if 'indent' not in new_styling:
                new_styling['indent'] = ''
            if 'list_level' not in new_styling:
                new_styling['list_level'] = 0
            if 'mark' not in new_styling:
                new_styling['mark'] = '• '
            new_styling['indent'] += '\t'
            new_styling['list_level'] += 1
        elif node.tag == 'ol':
            self.new_line(top_spacing + bottom_spacing)
            new_styling['indent'] = '\t'
            new_styling['list_level'] = 1
            new_styling[f'index{new_styling['list_level']}'] = 0
        elif node.tag == 'li':
            self.new_line(top_spacing + bottom_spacing)
            for style in styling:
                if style == 'foreground':
                    foreground = styling[style]
                elif style == 'size':
                    size = styling[style]
                elif style == 'font':
                    font = (styling[style],)
            font += (size,)

            text_element = self.canvas.create_text(
                (self.x_location + start_spacing, self.y_location + top_spacing),
                anchor=tk.NW,
                fill=foreground,
                text=new_styling['indent'] + new_styling['mark'],
                font=font
            )
            bounds = self.canvas.bbox(text_element)
            self.x_location = bounds[2]
            elements += (text_element,)
        elif node.tag == 'blockquote':
            self.new_line(top_spacing + bottom_spacing)
            new_styling['font'] = StyleDefaults.serifFont
            new_styling['background'] = StyleDefaults.pale_green
            new_styling['foreground'] = StyleDefaults.accentColour2
        elif node.tag == 'img':
            pass
        elif node.tag == 'data':
            text = node.get_attr("text")

            # load style instructions
            for style in styling:
                if style == 'foreground' or style == 'fg':
                    foreground = styling[style]
                elif style == 'background' or style == 'bg':
                    background = styling[style]
                elif style == 'size':
                    size = styling[style]
                elif style == 'font':
                    font = (styling[style],)
                elif style == 'underline':
                    underline = styling[style]
                elif style == 'bold':
                    bold = styling[style]
                elif style == 'italic':
                    italic = styling[style]

            font += (size,)

            # add style elements to the font
            if underline:
                font += ('underline',)
            if bold:
                font += ('bold',)
            if italic:
                font += ('italic',)

            text_element = self.canvas.create_text(
                (self.x_location + start_spacing, self.y_location + top_spacing),
                anchor=tk.NW,
                fill=foreground,
                text=text,
                font=font,
            )

            bounds = self.canvas.bbox(text_element)

            bg_element = self.canvas.create_rectangle((bounds[0], bounds[1]), (bounds[2], bounds[3]), fill=background)
            self.canvas.tag_lower(bg_element)
            # self.y_location = bounds[3] + bottom_spacing
            self.x_location = bounds[2] + end_spacing
            elements += ((text_element, bg_element),)

            self.line.append((text_element, bg_element))

        for child in node.children:
            elements += self.render_node(child, new_styling)

        # print(elements)
        return elements

    def new_line(self, line_spacing):
        self.lines.append(self.line)
        # self.line = []
        self.line_number += 1
        self.x_location = 0
        bottom_of_line = 0
        for element in self.line:
            text, bg = element
            bounds = self.canvas.bbox(text)
            if bounds[3] > bottom_of_line:
                bottom_of_line = bounds[3]
        self.y_location = bottom_of_line + line_spacing
