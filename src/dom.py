import sys
from urllib import request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

import base64
import re as re

import serialiser
from src import renderer


class HtmlNode:
    """
    Represents a tag or text element in a HTML document.
    """

    parent = None
    children = None
    tag = None
    attrs = None

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

    def delete(self):
        """
        Remove all children recursively, allowing nodes to be freed by the garbage collector.
        """
        self.parent = None
        for child in self.children:
            child.delete()
        self.children = list()


# Following are specialisations of HtmlNode

class ImgNode(HtmlNode):

    def __init__(self, parent, tag, attrs, url):
        super().__init__(parent, tag, attrs)
        self.image = None
        self.url = url
        if self.url is not None:
            src = self.get_attr('src')
            path = self.make_path(src)
            try:
                response = request.urlopen(path)
                data = response.read()
                self.attrs.append(('data', base64.b64encode(data).decode('utf-8')))
            except (HTTPError or URLError) as e:
                print(path, e)

    def make_path(self, image_path):
        proto, _, path = self.url.partition('://')
        # print("proto is " + proto)
        # print("_ is " + _)
        # print("path is " + image_path)
        if re.match(r'\w*:.*', image_path):
            # Full url
            return image_path
        elif image_path[0] + image_path[1] == '//':
            return 'https:' + image_path
        elif image_path[0] == '/':
            # Absolute path
            before, sep, after = path.partition('/')
            return proto + '://' + before + image_path
        else:
            # Relative path
            before, sep, after = path.rpartition('/')
            return proto + '://' + before + '/' + image_path


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
        if tag == 'img':
            node = ImgNode(self.parent, tag, attrs, self.url)
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

        self.renderer = renderer.Renderer(tk_frame)

        self.setup_mouse_wheel()

    def render(self):
        self.renderer.render(self.root)

    def setup_mouse_wheel(self):
        # Bet you didn't expect this to be so hard.
        # We have to do additional setup when the page is finished loading!
        top = self.tk_frame.winfo_toplevel()
        if sys.platform == 'linux':
            # Mouse wheel is implemented as buttons 4 (up) and 5 (down)!
            top.bind_class('scrolly', '<Button-4>',
                           lambda e: self.renderer.canvas.yview_scroll(-1, 'units'))
            top.bind_class('scrolly', '<Button-5>',
                           lambda e: self.renderer.canvas.yview_scroll(1, 'units'))
        else:
            top.bind_class('scrolly', '<MouseWheel>',
                           lambda e: self.renderer.canvas.yview_scroll(int(e.delta / -60), 'units'))

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



    def load_url(self, url):
        """
        Load a Html document from the internet.
        Note that UTF-8 encoding is assumed, and no other encoding is supported.
        :param url: The url to fetch the document from.
        """

        # Download the page
        self.address = url
        req = request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'})
        response = request.urlopen(req)

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


    def __str__(self):
        return "[" + str(self.title) + "](" + str(self.address) + ")"

    def find_nodes(self, selector):
        """
        Find all nodes on the page matching selector.
        Selector is a tag name, or None for all nodes
        :param selector: The selector to match
        :return: A list of matching nodes.
        """
        result = list()
        #self.root.find_nodes(result, selector)
        return result

    def find_children(self, *selectors):
        """
        Find nodes matching a chain of selectors.
        :param selectors: The selectors to match
        :return: List of nodes matching the chain.
        """
        # result = [self.root]
        result = []
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