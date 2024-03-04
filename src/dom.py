from urllib import request
from html.parser import HTMLParser

import tkinter as tk
import tkinter.ttk as ttk
import re as re


class HtmlNode:
    parent = None
    children = None
    tag = None
    attrs = None
    tk_object = None

    def __init__(self, parent, tag, attrs):
        self.parent = parent
        self.tag = tag
        self.attrs = attrs
        self.children = list()

    def __str__(self):
        text = "<" + self.tag + ">"
        for child in self.children:
            text += str(child)
        text += "</" + self.tag + ">"
        return text

    def add_child(self, node):
        self.children.append(node)

    def find_nodes(self, result, selector):
        if selector is None or self.tag == selector:
            result.append(self)
        for child in self.children:
            child.find_nodes(result, selector)

    def get_attr(self, attr):
        for a in self.attrs:
            if a[0] == attr:
                return a[1]
        return None

    def add_tk(self, parent, style):
        # print('node')
        frame = ttk.Frame(parent, style=style)
        for child in self.children:
            child.add_tk(frame, style)
        frame.grid(stick=tk.W)
        self.tk_object = frame
        return frame

    # Remove all children recursively, allowing nodes to be freed by the garbage collector
    def delete(self):
        self.parent = None
        for child in self.children:
            child.delete()
        self.children = list()


class HeadNode(HtmlNode):
    pass


class TitleNode(HtmlNode):
    def add_tk(self, parent, style):
        # label = ttk.Label(parent, text=self.children[0].get_attr("text"))
        # label.grid(stick=tk.W)
        # self.tk_object = label
        return None


class BodyNode(HtmlNode):
    def add_tk(self, parent, style):
        # print('body node')
        frame = ttk.Frame(parent, style=style)
        for child in self.children:
            child.add_tk(frame, style)
        frame.grid(sticky=tk.W)
        self.tk_object = frame
        return frame


class DivNode(HtmlNode):
    def add_tk(self, parent, style):
        self.tk_object = super().add_tk(parent, 'div.TLabel')
        return self.tk_object


class SpanNode(HtmlNode):
    def add_tk(self, parent, style):
        self.tk_object = super().add_tk(parent, 'span.TLabel')
        return self.tk_object


class ANode(HtmlNode):
    def add_tk(self, parent, style):
        self.tk_object = super().add_tk(parent, 'a.TLabel')
        self.tk_object.configure(cursor='hand2')
        return self.tk_object

    def a_clicked(self):
        pass


class TableNode(HtmlNode):
    pass

class PNode(HtmlNode):
    def add_tk(self, parent, style):
        return super().add_tk(parent, 'p.TLabel')


class PreNode(HtmlNode):
    pass


class HNode(HtmlNode):
    def __init__(self, parent, tag, attrs, h_level):
        super().__init__(parent, tag, attrs)
        self.h_level = h_level

    def add_tk(self, parent, style):
        frame = ttk.Frame(parent, style=style)
        for child in self.children:
            child.add_tk(frame, f'h{self.h_level}.TLabel')
        frame.grid(sticky=tk.W)
        self.tk_object = frame
        return frame


class HrNode(HtmlNode):
    def add_tk(self, parent, style):
        line_break = ttk.Label(parent, text='--------------------------------\n', style='hr.TLabel')
        line_break.grid(stick=tk.W)
        return line_break


class BrNode(HtmlNode):
    def add_tk(self, parent, style):
        line_break = ttk.Label(parent, text='\n', style='br.TLabel')
        line_break.grid(stick=tk.W)
        return line_break


class ImgNode(HtmlNode):
    pass


class DataNode(HtmlNode):
    def add_tk(self, parent, style):
        self.attrs.append(('style', style))
        label = ttk.Label(parent, text=self.get_attr("text"), style=style)
        self.tk_object = label
        label.grid(stick=tk.W)
        return label


def is_void(tag):
    return tag in ['area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                   'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']


class GaudyParser(HTMLParser):
    root = None
    parent = None

    def handle_starttag(self, tag, attrs):
        node = None
        if tag == 'head':
            node = HeadNode(self.parent, tag, attrs)
        elif tag == 'title':
            node = TitleNode(self.parent, tag, attrs)
        elif tag == 'body':
            node = BodyNode(self.parent, tag, attrs)
        elif tag == 'div':
            node = DivNode(self.parent, tag, attrs)
        elif tag == 'span':
            node = SpanNode(self.parent, tag, attrs)
        elif tag == 'a':
            node = ANode(self.parent, tag, attrs)
        elif tag == 'table':
            node = TableNode(self.parent, tag, attrs)
        elif tag == 'p':
            node = PNode(self.parent, tag, attrs)
        elif tag == 'pre':
            node = PreNode(self.parent, tag, attrs)
        elif tag == 'h1' or tag == 'h2' or tag == 'h3' or tag == 'h4' or tag == 'h5' or tag == 'h6':
            node = HNode(self.parent, tag, attrs, tag[1])
        elif tag == 'hr':
            node = HrNode(self.parent, tag, attrs)
        elif tag == 'br':
            node = BrNode(self.parent, tag, attrs)
        elif tag == 'img':
            node = ImgNode(self.parent, tag, attrs)
        elif tag == 'data':
            node = DataNode(self.parent, tag, attrs)
        else:
            node = HtmlNode(self.parent, tag, attrs)

        if self.parent is not None:
            self.parent.add_child(node)
        if not is_void(tag):
            self.parent = node
        if self.root is None:
            self.root = node

    def handle_endtag(self, tag):
        if not is_void(tag):
            self.parent = self.parent.parent

    def handle_data(self, data):
        if not data.isspace():
            data = re.sub(r'\s+', ' ', data)
            self.handle_starttag("data", [("text", data)])
            self.handle_endtag("data")


class HtmlPage:
    root = None
    address = None
    title = None
    tk_frame = None
    scrollbar = None
    scroll_canvas = None
    scroll_frame = None

    def __init__(self, url, tk_frame):
        self.tk_frame = tk_frame
        self.address = url

        self.scroll_canvas = tk.Canvas(self.tk_frame)
        self.scroll_frame = ttk.Frame(self.scroll_canvas, style='Gaudy.TFrame')
        self.scrollbar = tk.Scrollbar(self.tk_frame, orient="vertical", command=self.scroll_canvas.yview)

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(column=1, row=0, sticky=tk.NSEW)
        self.scroll_canvas.grid(column=0, row=0, sticky=tk.NSEW)
        self.scroll_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.tk_frame.grid_rowconfigure(0, weight=1)
        self.tk_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        self.scroll_frame.bind("<Configure>", self.function)

        response = request.urlopen(url)

        parser = GaudyParser()
        parser.feed(response.read().decode("utf-8"))
        self.root = parser.root

        title_string = ""
        title_datas = self.find_children("title", "data")
        for data in title_datas:
            title_string += data.get_attr("text")
        self.title = url if title_string.isspace() else title_string

        self.root.add_tk(self.scroll_frame, style='Gaudy.TFrame')

    def function(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"), width=1000, height=500)

    def __str__(self):
        return "[" + str(self.title) + "](" + str(self.address) + ")"

    def find_nodes(self, selector):
        result = list()
        self.root.find_nodes(result, selector)
        return result

    def find_children(self, *selectors):
        result = [self.root]
        for selector in selectors:
            scratch = list()
            for node in result:
                node.find_nodes(scratch, selector)
            result = scratch
        return result

    # Call before discarding a page to allow nodes to be freed
    def delete(self):
        if self.tk_frame is not None:
            self.tk_frame.destroy()
        if self.root is not None:
            self.root.delete()
