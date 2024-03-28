import base64
import copy
import tkinter as tk
import tkinter.ttk as ttk

from styleDefaults import StyleDefaults


def load_font_style(styling):
    font = (styling['font'], styling['size'])

    # add style elements to the font
    if styling['underline']:
        font += ('underline',)
    if styling['bold']:
        font += ('bold',)
    if styling['italic']:
        font += ('italic',)

    return font


class Renderer:
    default_style = {
        'font': StyleDefaults.primaryFont,
        'size': StyleDefaults.defaultFontSize,
        'foreground': StyleDefaults.defaultColour,
        'background': StyleDefaults.backgroundColour,
        'border_width': StyleDefaults.bg_border_width,
        'border_colour': StyleDefaults.bg_border_colour,
        'underline': False,
        'bold': False,
        'italic': False,
        'top_spacing': StyleDefaults.top_spacing,
        'bottom_spacing': StyleDefaults.bottom_spacing,
        'start_spacing': StyleDefaults.start_spacing,
        'end_spacing': StyleDefaults.end_spacing
    }

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
        # print('render ' + root.tag)
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

        self.render_node(root, self.default_style)

    def render_node(self, node, styling):
        new_styling = copy.deepcopy(styling)
        elements = tuple()
        # load font
        font = load_font_style(styling)

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
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
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
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])

        elif node.tag == 'p':
            block_level = True
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])

        elif node.tag == 'pre':
            new_styling['font'] = StyleDefaults.monospaceFont

        elif (node.tag == 'h1' or node.tag == 'h2' or node.tag == 'h3' or node.tag == 'h4' or node.tag == 'h5'
              or node.tag == 'h6'):
            block_level = True
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
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
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
            line = self.canvas.create_line((0, self.y_location + (styling['size'] / 2)),
                                           (0, self.y_location + (styling['size'] / 2)),
                                           width=1, fill=styling['foreground'])

            bg = self.canvas.create_rectangle((0 + styling['start_spacing'], self.y_location),
                                              (0 + styling['start_spacing'], self.y_location + styling['size']),
                                              width=styling['border_width'], fill=styling['background'],
                                              outline=styling['border_colour'])
            self.canvas.tag_raise(line)

            el = (line, bg)
            elements += el
            self.post_render["hr"].append(el)
            self.elements_in_page_order.append(el)

        elif node.tag == 'br':
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])

        elif node.tag == 'ul':
            block_level = True
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
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
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
            new_styling['indent'] = '\t'
            new_styling['list_level'] = 1
            new_styling[f'index{new_styling['list_level']}'] = 0

        elif node.tag == 'li':
            block_level = True
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
            text_element = self.canvas.create_text(
                (self.x_location + styling['start_spacing'], self.y_location + styling['top_spacing']),
                anchor=tk.NW,
                fill=styling['foreground'],
                text=styling['indent'] + styling['mark'],
                font=font
            )
            bounds = self.canvas.bbox(text_element)
            bg = self.canvas.create_rectangle((bounds[0], bounds[1]), (bounds[2], bounds[3]),
                                              width=styling['border_width'], fill=styling['background'],
                                              outline=styling['border_colour'])
            self.canvas.tag_raise(text_element)
            self.x_location = bounds[2]
            elements += (text_element, bg)

        elif node.tag == 'blockquote':
            block_level = True
            self.new_line(styling['top_spacing'] + styling['bottom_spacing'])
            new_styling['font'] = StyleDefaults.serifFont
            new_styling['background'] = StyleDefaults.pale_green
            new_styling['foreground'] = StyleDefaults.accentColour2

        elif node.tag == 'img':
            elements += self.render_image(node, new_styling)

        elif node.tag == 'data':
            text = node.get_attr("text")

            text_element = self.canvas.create_text(
                (self.x_location + styling['start_spacing'], self.y_location + styling['top_spacing']),
                anchor=tk.NW,
                fill=styling['foreground'],
                text=text,
                font=font,
            )
            bounds = self.canvas.bbox(text_element)
            bg_element = self.canvas.create_rectangle((bounds[0], bounds[1]), (bounds[2], bounds[3]),
                                                      width=styling['border_width'], fill=styling['background'],
                                                      outline=styling['border_colour'])
            self.canvas.tag_raise(text_element)
            self.x_location = bounds[2] + styling['end_spacing']
            elements += ((text_element, bg_element),)

            # self.canvas.tag_bind()

            self.elements_in_page_order.append((text_element, bg_element))

        for child in node.children:
            elements += self.render_node(child, new_styling)

        if block_level:
            self.new_line(styling['bottom_spacing'] + styling['top_spacing'])
        if link:
            self.post_render["a"].append((node.get_attr('href'), elements))
        # print(node)
        # print(elements)
        return elements

    def render_image(self, node, styling):
        font = load_font_style(styling)
        node.image = None
        title = node.get_attr('title')
        alt = node.get_attr('alt')

        if node.get_attr('data') is not None:
            try:
                node.image = tk.PhotoImage(data=base64.b64decode(node.get_attr('data')))
            except tk.TclError:
                pass

        img = None

        if node.image is None:
            node.image = tk.PhotoImage(file="icons/icons8-unavailable-48.png")
            img = self.canvas.create_text((self.x_location + styling['start_spacing'],
                                           self.y_location + styling['top_spacing']),
                                          anchor=tk.NW,
                                          text=alt,
                                          font=font,
                                          fill=styling['foreground']
                                          )
        else:
            img = self.canvas.create_image((self.x_location + styling['start_spacing'],
                                            self.y_location + styling['top_spacing']),
                                           anchor=tk.NW,
                                           image=node.image)
        if title is None:
            title = 'no title'

        img_bounds = self.canvas.bbox(img)
        t = self.canvas.create_text((img_bounds[0], img_bounds[3]),
                                    anchor=tk.NW,
                                    text=title,
                                    font=font,
                                    fill=styling['foreground'])
        t_bounds = self.canvas.bbox(t)
        bounds = self.canvas.bbox(img, t)
        bg = self.canvas.create_rectangle(bounds,
                                          width=styling['border_width'], fill=styling['background'],
                                          outline=styling['border_colour'])
        self.canvas.tag_raise(img, bg)
        self.canvas.tag_raise(t, bg)

        return img, t, bg

    def new_line(self, line_spacing):
        self.line_number += 1
        self.x_location = 0
        bounds = self.canvas.bbox('all')
        if bounds is not None:
            self.y_location = bounds[3] + line_spacing

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

    def bind_links(self, conductor):
        for a in self.post_render["a"]:
            bind = lambda c, tag, link: self.canvas.tag_bind(tag, "<Button-1>", lambda event: c.go(link))
            href, elements = a
            path = conductor.make_path(href)
            # print('elements' + str(elements))
            for element in elements:
                # print('element' + str(element))
                item = None
                bg = None
                if type(element) is not tuple:
                    pass
                    # print(element)
                    # print('not tuple')
                elif len(element) == 2:
                    item, bg = element
                    bind(conductor, item, path)
                    bind(conductor, bg, path)
                elif len(element) == 3:  # image in link
                    item, title, bg = element
                    bind(conductor, title, path)
                    bind(conductor, item, path)
                    bind(conductor, bg, path)
                # print(item)
                # print(path)
