from urllib import request
from html.parser import HTMLParser

import tkinter as tk
import tkinter.ttk as ttk


class HtmlNode:
    parent = None
    children = None
    tag = None
    attrs = None

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

    def add_tk(self, parent):
        label = None
        if self.tag == 'data':
            label = (ttk.Label(parent, text=self.get_attr("text")))
            label.pack()
        for child in self.children:
            child.add_tk(parent)
        return label

    # Remove all children recursively, allowing nodes to be freed by the garbage collector
    def delete(self):
        self.parent = None
        for child in self.children:
            child.delete()
        self.children = list()


class GaudyParser(HTMLParser):
    root = None
    parent = None

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(self.parent, tag, attrs)
        if self.parent is not None:
            self.parent.add_child(node)
        self.parent = node
        if self.root is None:
            self.root = node

    def handle_endtag(self, tag):
        self.parent = self.parent.parent

    def handle_data(self, data):
        if not data.isspace():
            self.handle_starttag("data", [("text", data)])
            self.handle_endtag("data")


class HtmlPage:
    root = None
    address = None
    title = None

    def __init__(self, url):
        self.address = url
        response = request.urlopen(url)

        parser = GaudyParser()
        parser.feed(response.read().decode("utf-8"))
        self.root = parser.root

        title_string = ""
        title_datas = self.find_children("title", "data")
        for data in title_datas:
            title_string += data.get_attr("text")
        self.title = url if title_string.isspace() else title_string

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

    def add_tk(self, parent):
        page_frame = ttk.Frame(parent)
        self.root.add_tk(page_frame)
        return page_frame

    # Call before discarding a page to allow nodes to be freed
    def delete(self):
        if self.root is not None:
            self.root.delete()


if __name__ == "__main__":
    page = HtmlPage("https://example.com")
    print(page)
    print(page.root)
    page.delete()
