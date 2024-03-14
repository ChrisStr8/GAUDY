from urllib import request
from urllib.error import URLError
from html.parser import HTMLParser

import base64

from http.client import HTTPException

import tkinter as tk
import tkinter.ttk as ttk
import re as re

from src import serialiser


class HtmlNode:
    """
    Represents a tag or text element in a HTML document.
    """

    parent = None
    children = None
    tag = None
    attrs = None
    tk_object = None

    def __init__(self, parent, tag, attrs):
        """
        Create a new node
        :param parent: Containing node - None for top-level <html> tag
        :param tag: Name of tag. Special value 'data' used for text nodes.
        :param attrs: List of key-value pairs of attributes.
        """
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
        """
        Add a child node to this tag.
        :param node: The child to add
        """
        self.children.append(node)

    def find_nodes(self, result, selector):
        """
        Add child nodes matching the given selector to the result list.
        Selector is a tag name.
        Modifies the 'result' list!
        :param result: The list where matches are added
        :param selector: The tag type to search for.
        """
        if selector is None or self.tag == selector:
            result.append(self)
        for child in self.children:
            child.find_nodes(result, selector)

    def get_attr(self, attr):
        """
        Find the value of an attribute on this node.
        :param attr: The attribute to retrieve
        :return: The value of the attribute, or None if not found
        """
        for a in self.attrs:
            if a[0] == attr:
                return a[1]
        return None

    def clear_attr(self, attr):
        for a in self.attrs:
            if a[0] == attr:
                self.attrs.remove(a)

    def add_tk(self, parent, style, indent, dot):
        """
        Add a Tk frame to represent this tag.
        :param parent: The Parent Tk frame.
        :param style: The style string to use.
        :param indent: an int denoting the level of indentation
        :param dot: the character to use for list elements
        :return: The frame added.
        """

        frame = ttk.Frame(parent, style=style)

        # Recursively call add_tk to create tk controls for children.
        for child in self.children:
            s = style
            if child.tag == 'data' and not re.match(r'.*TLabel', s):
                s = 'p.TLabel'
            child.add_tk(frame, s, indent, dot)

        frame.grid(sticky=tk.W)
        self.tk_object = frame
        return frame

    def delete(self):
        """
        Remove all children recursively, allowing nodes to be freed by the garbage collector.
        """
        self.parent = None
        for child in self.children:
            child.delete()
        self.children = list()

# Following are specialisations of HtmlNode


class HeadNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Don't render any children of <head>
        pass


class TitleNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Don't render any children of <title>
        return None


class BodyNode(HtmlNode):
    pass


class DivNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Call HtmlNode.add_tk with alternate style
        return super().add_tk(parent, 'div.TLabel', indent, dot)


class SpanNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Call HtmlNode.add_tk with alternate style
        return super().add_tk(parent, 'span.TLabel', indent, dot)


class ANode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Call HtmlNode.add_tk with alternate style.
        super().add_tk(parent, 'a.TLabel', indent, dot)

        # Set cursor to pointing hand when hovering over a link.
        self.tk_object.configure(cursor='hand2')
        return self.tk_object


class TableNode(HtmlNode):
    pass


class PNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Call HtmlNode.add_tk with alternate style
        return super().add_tk(parent, 'p.TLabel', indent, dot)


class PreNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Call HtmlNode.add_tk with alternate style
        return super().add_tk(parent, 'pre.TLabel', indent, dot)


class HNode(HtmlNode):
    """
    All heading levels (h1 - h6) use this class.
    """

    def __init__(self, parent, tag, attrs, h_level):
        """
        Create a heading node with given level (1 - 6)
        :param parent: Containing node - None for top-level <html> tag
        :param tag: Name of tag. Special value 'data' used for text nodes.
        :param attrs: List of key-value pairs of attributes.
        :param h_level: Level of node (1 - 6)
        """
        super().__init__(parent, tag, attrs)
        self.h_level = h_level

    def add_tk(self, parent, style, indent, dot):
        # Call HtmlNode.add_tk with correct heading style
        return super().add_tk(parent, f'h{self.h_level}.TLabel', indent, dot)


class HrNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Draw a Horizontal Line
        line_break = ttk.Label(parent, text='--------------------------------', style='hr.TLabel')
        line_break.grid(stick=tk.W)
        return line_break


class BrNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Force a line break
        line_break = ttk.Label(parent, text='', style='br.TLabel')
        line_break.grid(stick=tk.W)
        return line_break


class ImgNode(HtmlNode):

    def __init__(self, parent, tag, attrs, url):
        super().__init__(parent, tag, attrs)
        self.image = None
        self.url = url

    def make_path(self, image_path):
        if re.match(r'\w*:.*', image_path):
            return image_path

        addr = self.url
        before, sep, after = addr.rpartition('/')

        return before + '/' + image_path

    def add_tk(self, parent, style, indent, dot):
        if self.url is not None:
            src = self.get_attr('src')
            try:
                response = request.urlopen(self.make_path(src))
                self.attrs.append(('data', base64.b64encode(response.read()).decode('utf-8')))
            except HTTPException or URLError:
                pass

        if self.get_attr('data') is not None:
            try:
                self.image = tk.PhotoImage(data=base64.b64decode(self.get_attr('data')))
            except tk.TclError:
                pass

        if self.image is None:
            self.image = tk.PhotoImage(file="icons/icons8-unavailable-48.png")

        panel = ttk.Label(parent, image=self.image)
        panel.grid()
        return panel


class UlNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        return super().add_tk(parent, style, indent + '\t', '•')


class DataNode(HtmlNode):
    def add_tk(self, parent, style, indent, dot):
        # Create a label with the node's text
        self.attrs.append(('style', style))
        label = ttk.Label(parent, text=(indent + dot + self.get_attr("text")), style=style)
        self.tk_object = label
        label.grid(stick=tk.W)
        return label

    def append(self, text):
        new_text = self.get_attr('text') + text
        self.clear_attr('text')
        self.attrs.append(('text', new_text))


def is_void(tag):
    """
    Void tags are those that are not permitted to have children.
    These may be written as eg. <br> or <br /> - we treat them equivalently.
    :param tag: The tag to check.
    :return: True if tag is a void tag, otherwise False
    """
    return tag in ['area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                   'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']


class GaudyParser(HTMLParser):
    """
    Specialisation of Python's built-in HTMLParser to convert Html document into an internal representation. This
    will create the page structure. This assumes that the page data represents valid HTML5. Non-standard or
    deprecated features (such as <blink> or <marquee> tags, or implicitly closed tags) are not supported.
    """

    # Page root element (ie. the top-level <html> tag)
    root = None

    # Current parent node to which children are being added.
    parent = None

    def __init__(self, url):
        super().__init__()
        self.url = url

    def last_child(self):
        if len(self.parent.children) == 0:
            return None
        else:
            return self.parent.children[-1]

    def match_last_child(self, tag):
        return self.last_child() is not None and self.last_child().tag == tag

    def handle_starttag(self, tag, attrs):
        """
        Create a tag.
        :param tag: Name of tag
        :param attrs: List of key-value pairs of attributes
        """
        node = None

        # Choose which specialisation of HtmlNode to create
        # Unrecognised tags use the base HtmlNode.
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
            # Don't insert a new node for br between data
            if self.match_last_child('data'):
                self.last_child().append('\n')
            else:
                node = BrNode(self.parent, tag, attrs)
        elif tag == 'img':
            node = ImgNode(self.parent, tag, attrs, self.url)
        elif tag == 'data':
            node = DataNode(self.parent, tag, attrs)
        elif tag == 'ul':
            node = UlNode(self.parent, tag, attrs)
        else:
            node = HtmlNode(self.parent, tag, attrs)

        if node is None:
            return

        # Add the new node to the parent (if it is not the top-level node)
        if self.parent is not None:
            self.parent.add_child(node)

        # If the new tag is not a void tag, then set it to be the current parent
        if not is_void(tag):
            self.parent = node

        # If this is the top-level node, then make it root
        if self.root is None:
            self.root = node

    def handle_endtag(self, tag):
        """
        Close a tag.
        :param tag: The tag being closed
        """

        # If this is not a void tag, then set the parent to its parent.
        # This will cause new tags to be siblings of the current parent tag.
        # Void tags were never made parent, so they can be ignored.
        if not is_void(tag):
            self.parent = self.parent.parent

    def handle_data(self, data):
        """
        Create a data node by calling handle_starttag and handle_endtag
        :param data: The raw text to be added.
        """

        # If the data is entirely whitespace (or empty!) then skip it.
        if len(data) > 0 and not data.isspace():
            # Replace sequences of whitespace characters in data with a single blank.
            data = re.sub(r'\s+', ' ', data)

            if self.match_last_child('data'):
                # Multiple sequential data nodes (this can occur after br tags in some cases)
                self.last_child().append(data)
            else:
                # Call handle_starttag and handle_endtag to create the data node.
                # The node is given an attribute 'text' which contains the data.
                self.handle_starttag("data", [("text", data)])
                self.handle_endtag("data")


class HtmlPage:
    """
    Represents a Html Document.
    """

    def __init__(self, tk_frame):
        """
        Create a new HtmlPage. Call load_url or load_data to set the page content.
        :param tk_frame: The frame to create components and draw in.
        """

        self.root = None
        self.title = ""
        self.address = ""
        self.tk_frame = tk_frame

        # Create top-level components - Canvas, Scrollbar, and Frame
        self.scroll_canvas = tk.Canvas(self.tk_frame)
        self.scroll_frame = ttk.Frame(self.scroll_canvas, style='Gaudy.TFrame')
        self.scrollbar = tk.Scrollbar(self.tk_frame, orient="vertical", command=self.scroll_canvas.yview)

        # Layout components
        self.scrollbar.grid(column=1, row=0, sticky=tk.NSEW)
        self.scroll_canvas.grid(column=0, row=0, sticky=tk.NSEW)
        self.scroll_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.tk_frame.grid_rowconfigure(0, weight=1)
        self.tk_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        # Associate the canvas and scrollbar
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        self.scroll_frame.bind("<Configure>", self.configure_scroll_frame)

    def finish_loading(self, parser):
        """
        Finalise page loading after a call to load_url or load_data
        :param parser: The GaudyParser that created the page
        """

        # Set the page root element
        self.root = parser.root

        # Set the page title. This will be the text of any <title> tags, or the page url if there are none Although
        # multiple <title> tags in one document aren't permitted by the HTML Specification, we handle it by
        # concatenating them.
        title_string = ""
        title_datas = self.find_children("title", "data")
        for data in title_datas:
            title_string += data.get_attr("text")
        self.title = self.address if title_string.isspace() else title_string

        # Draw the page by creating Tk controls for each tag.
        self.root.add_tk(self.scroll_frame, style='Gaudy.TFrame', indent='', dot='')

    def load_url(self, url):
        """
        Load a Html document from the internet.
        Note that UTF-8 encoding is assumed, and no other encoding is supported.
        :param url: The url to fetch the document from.
        """

        # Download the page
        self.address = url
        response = request.urlopen(url)

        # Create Html Node structure
        parser = GaudyParser(url)
        parser.feed(response.read().decode("utf-8"))

        # Finalise loading
        self.finish_loading(parser)

    def load_data(self, data):
        """
        Load a Html Document from serialised data.
        :param data: The serialised data to convert back into a page.
        """

        # Use the deserialiser to recreate the page.
        parser = GaudyParser(None)
        hd = serialiser.HtmlDeserialiser(parser, data)
        self.address = hd.address

        # Finalise loading
        self.finish_loading(parser)

    def configure_scroll_frame(self, event):
        """
        Scroll frame is being configured, ie. scrolled!
        :param event: Tk event data
        """
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"), width=800, height=600)

    def __str__(self):
        return "[" + str(self.title) + "](" + str(self.address) + ")"

    def find_nodes(self, selector):
        """
        Find all nodes on the page matching selector.
        Selector is a tag name.
        :param selector: The selector to match
        :return: A list of matching nodes.
        """
        result = list()
        self.root.find_nodes(result, selector)
        return result

    def find_children(self, *selectors):
        """
        Find nodes matching a chain of selectors.
        :param selectors: The selectors to match
        :return: List of nodes matching the chain.
        """
        result = [self.root]
        for selector in selectors:
            scratch = list()
            for node in result:
                node.find_nodes(scratch, selector)
            result = scratch
        return result

    def delete(self):
        """
        HtmlNodes contain a reference to their pointer, preventing them from being cleaned up by Python's garbage
        collector (which uses reference counting). Call this to clear this parent reference. Likewise destroy the Tk
        elements associated with the page. :return:
        """
        if self.tk_frame is not None:
            self.tk_frame.destroy()
        if self.root is not None:
            self.root.delete()


def create_page_from_url(url, frame):
    """
    Create a page object from the given url, in the given frame.
    :param url: The url to access the page data.
    :param frame: The Tk frame to draw the page into.
    :return: An HtmlPage object.
    """
    page = HtmlPage(frame)
    page.load_url(url)
    return page


def deserialise_page(data, frame):
    """
    Recreate a html page from serialised data.
    :param data: The saved page data.
    :param frame: The Tk frame to draw the page into.
    :return: An HtmlPage object.
    """
    page = HtmlPage(frame)
    page.load_data(data)
    return page
