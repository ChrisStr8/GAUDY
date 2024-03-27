import copy
import tkinter as tk
import tkinter.ttk as ttk

from styleDefaults import StyleDefaults


class Renderer:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg=StyleDefaults.backgroundColour, )

        self.scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)

        self.scrollbar.grid(column=1, row=0, sticky=tk.NSEW)
        self.canvas.grid(column=0, row=0, sticky=tk.NSEW)

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", self.reconfigure_canvas)
        self.canvas.bindtags(('scrolly',) + self.canvas.bindtags())

        self.x_location = 0
        self.y_location = 0
        self.elements_in_page_order = []
        self.line_number = 0
        self.post_render = {
            "a": [],
            "hr": []
        }

    def render(self, root):
        # reset canvas
        self.canvas.delete('all')
        # reset position for rendering
        self.line_number = 0
        self.x_location = 0
        self.y_location = 0
        # reset post rendered elements
        self.post_render = {
            "a": [],
            "hr": []
        }

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
        bg_border_width = StyleDefaults.bg_border_width
        bg_border_colour = StyleDefaults.bg_border_colour
        underline = False
        bold = False
        italic = False

        block_level = False
        link = False

        if node.tag == 'head':
            pass
        elif node.tag == 'title':
            return tuple()
        elif node.tag == 'body':
            pass
        elif node.tag == 'div':
            block_level = True
            self.new_line(top_spacing + bottom_spacing)
            new_styling['font'] = StyleDefaults.userInterfaceFont
            new_styling['foreground'] = StyleDefaults.primaryColour
        elif node.tag == 'span':
            new_styling['italic'] = True
        elif node.tag == 'a':
            link = True
            new_styling['foreground'] = StyleDefaults.link_colour
            new_styling['underline'] = True
        elif node.tag == 'table':
            block_level = True
            self.new_line(top_spacing + bottom_spacing)
        elif node.tag == 'p':
            block_level = True
            self.new_line(top_spacing + bottom_spacing)
        elif node.tag == 'pre':
            new_styling['font'] = StyleDefaults.monospaceFont
        elif (node.tag == 'h1' or node.tag == 'h2' or node.tag == 'h3' or node.tag == 'h4' or node.tag == 'h5'
              or node.tag == 'h6'):
            block_level = True
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
            block_level = True
            # print('test hr')
            self.new_line(top_spacing + bottom_spacing)
            # print(" width: " + str(self.canvas.winfo_width()))
            line = self.canvas.create_line((0, self.y_location + (size / 2)),
                                           (0, self.y_location + (size / 2)),
                                           width=1, fill=foreground)

            bg = self.canvas.create_rectangle((0 + start_spacing, self.y_location),
                                              (0 + start_spacing, self.y_location + size),
                                              width=bg_border_width, fill=background, outline=bg_border_colour)
            self.canvas.tag_raise(line)

            el = (line, bg)
            elements += el
            self.post_render["hr"].append(el)
            self.elements_in_page_order.append(el)

        elif node.tag == 'br':
            self.new_line(top_spacing + bottom_spacing)
        elif node.tag == 'ul':
            block_level = True
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
            block_level = True
            self.new_line(top_spacing + bottom_spacing)
            new_styling['indent'] = '\t'
            new_styling['list_level'] = 1
            new_styling[f'index{new_styling['list_level']}'] = 0
        elif node.tag == 'li':
            block_level = True
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
            bg = self.canvas.create_rectangle((bounds[0], bounds[1]), (bounds[2], bounds[3]),
                                              width=bg_border_width, fill=background, outline=bg_border_colour)
            self.x_location = bounds[2]
            elements += (text_element, bg)
        elif node.tag == 'blockquote':
            block_level = True
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

            bg_element = self.canvas.create_rectangle((bounds[0], bounds[1]), (bounds[2], bounds[3]),
                                                      width=bg_border_width, fill=background, outline=bg_border_colour)
            self.canvas.tag_lower(bg_element)
            # self.y_location = bounds[3] + bottom_spacing
            self.x_location = bounds[2] + end_spacing
            elements += ((text_element, bg_element),)

            # self.canvas.tag_bind()

            self.elements_in_page_order.append((text_element, bg_element))

        for child in node.children:
            elements += self.render_node(child, new_styling)

        if block_level:
            self.new_line(bottom_spacing + top_spacing)
        if link:
            self.post_render["a"].append((node.get_attr('href'), elements))
        return elements

    def new_line(self, line_spacing):
        self.line_number += 1
        self.x_location = 0
        bottom_of_line = 0
        for element in self.elements_in_page_order:
            text, bg = element
            bounds = self.canvas.bbox(bg)
            if bounds[3] > bottom_of_line:
                bottom_of_line = bounds[3]
        self.y_location = bottom_of_line + line_spacing

    def reconfigure_canvas(self, event):
        """
        Canvas is being configured e.g. window size changes
        :param event: Tk event data
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.adjust_to_dimensions(self.canvas.winfo_width(), self.canvas.winfo_height())

    def adjust_to_dimensions(self, width, height):
        for hr in self.post_render["hr"]:
            line, bg = hr
            x0, y0, x1, y1 = self.canvas.coords(bg)
            # print((x0, y0, x1, y1))
            self.canvas.coords(bg, x0, y0, width, y1)

            lx0, ly0, lx1, ly1 = self.canvas.coords(line)
            self.canvas.coords(line, x0 + (width * 0.1), ly0, width - (width * 0.1), ly1)

    def bind_links(self, context):
        for a in self.post_render["a"]:
            href, elements = a
