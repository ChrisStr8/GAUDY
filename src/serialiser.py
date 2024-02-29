from dom import HtmlPage, HtmlNode

OBJECT = b'\x00'
FIELD = b'\x01'
TEXT_VALUE = b'\x02'
LIST_VALUE = b'\x03'
END_LIST_VALUE = b'\x04'

class Serialiser:

    def __init__(self):
        self.result = bytearray()

    def write(self, data: bytes):
        self.result.extend(data)
        return self

    def object(self, name: bytes):
        self.write(OBJECT)
        self.write(name)
        return self

    def field(self, name: bytes):
        self.write(FIELD)
        self.write(name)
        return self

    def text(self, text: str):
        self.write(TEXT_VALUE)
        data = text.encode('utf-8')

        # TODO: Replace control sequences in encoded text with escape sequence

        self.write(data)
        return self

    def start_list(self):
        self.write(LIST_VALUE)
        return self

    def end_list(self):
        self.write(END_LIST_VALUE)
        return self

    def html_node(self, node: HtmlNode):
        tk = node.tk_object
        self.object(node.tag.encode('utf-8'))
        if tk is not None:
            self.field(b'tk_object').text(tk.widgetName)

        if len(node.attrs) > 0:
            self.field(b'attr').start_list()
            for attr in node.attrs:
                self.field(attr[0].encode('utf-8')).text(attr[1])
            self.end_list()

        if len(node.children) > 0:
            self.field(b'children').start_list()
            for child in node.children:
                self.html_node(child)
            self.end_list()

        return self

    def page(self, page: HtmlPage):
        self.object(b'page')
        self.field(b'title').text(page.title)
        self.field(b'address').text(page.address)
        self.field(b'root').html_node(page.root)

    def get_bytes(self):
        return bytes(self.result)


def bytes_from_html(page: HtmlPage) -> bytes:
    s = Serialiser()
    s.page(page)
    return s.get_bytes()
