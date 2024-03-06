from builtins import ValueError

from html.parser import HTMLParser

OBJECT = b'\x00'
END_OBJECT = b'\x01'
FIELD = b'\x02'
TEXT_VALUE = b'\x03'
LIST_VALUE = b'\x04'
END_LIST_VALUE = b'\x05'


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

    def end_object(self):
        self.write(END_OBJECT)

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

    def html_node(self, node):
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

        self.end_object()
        return self

    def page(self, page):
        self.object(b'page')
        self.field(b'title').text(page.title)
        self.field(b'address').text(page.address)
        self.field(b'root').html_node(page.root)
        self.end_object()

    def get_bytes(self):
        return bytes(self.result)


def bytes_from_html(page) -> bytes:
    s = Serialiser()
    s.page(page)
    return s.get_bytes()


class SerialisationError(Exception):
    pass


class DeserialisedObject:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def find(self, name):
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def __str__(self):
        return f'({self.name}, {str([str(f) for f in self.fields])})'


class DeserialisedList:
    def __init__(self, value):
        self.value = value

    def find(self, name):
        for v in self.value:
            if v.name == name:
                return v
        return None

    def __str__(self):
        return str([v.name for v in self.value])


class DeserialisedField:
    def __init__(self, name, value_type, value):
        self.name = name
        self.value_type = value_type
        self.value = value

    def find(self, name):
        if self.value_type == LIST_VALUE or self.value_type == OBJECT:
            return self.value.find(name)
        else:
            return None

    def text(self):
        if self.value_type == TEXT_VALUE:
            return self.value
        else:
            return None

    def list(self):
        if self.value_type == LIST_VALUE:
            return self.value.value
        else:
            return None

    def __str__(self):
        return f'{self.name}: {self.value}'


class Deserialiser:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def peek(self):
        try:
            return self.data[self.index].to_bytes()
        except IndexError as error:
            raise SerialisationError from error

    def read(self):
        b = self.peek()
        self.index += 1
        return b

    def read_text(self, expected: bytes):
        self.expect(expected)
        object_name = bytearray()
        while self.peek()[0] >= 0x20:
            object_name.append(self.read()[0])

        return object_name.decode('utf-8')

    def expect(self, value: bytes):
        for b in value:
            if self.peek()[0] != b:
                print('Expected: ', value)
                print(self.peek()[0], b)
                raise SerialisationError
            self.read()
        return self

    def parse_object(self):
        name = self.read_text(OBJECT)
        fields = list()
        while self.peek() != END_OBJECT:
            fields.append(self.parse_field())
        self.expect(END_OBJECT)
        return DeserialisedObject(name, fields)

    def parse_field(self):
        field_name = self.read_text(FIELD)
        if self.peek() == TEXT_VALUE:
            value = self.read_text(TEXT_VALUE)
            value_type = TEXT_VALUE
        elif self.peek() == LIST_VALUE:
            value = self.list_value()
            value_type = LIST_VALUE
        elif self.peek() == OBJECT:
            value = self.parse_object()
            value_type = OBJECT
        else:
            raise SerialisationError
        return DeserialisedField(field_name, value_type, value)

    def list_value(self):
        value = list()
        self.expect(LIST_VALUE)
        while self.peek() != END_LIST_VALUE:
            if self.peek() == FIELD:
                value.append(self.parse_field())
            elif self.peek() == OBJECT:
                value.append(self.parse_object())
            else:
                raise SerialisationError
        self.expect(END_LIST_VALUE)
        return DeserialisedList(value)


def get_attrs(encoded_attrs):
    attrs = list()
    if encoded_attrs is not None:
        for a in encoded_attrs.list():
            attrs.append((a.name, a.text()))
    return attrs


class HtmlDeserialiser:

    def __init__(self, parser: HTMLParser, raw: bytes):
        self.data = Deserialiser(raw).parse_object()
        if self.data.name != 'page':
            raise SerialisationError
        page = self.data
        self.parser = parser
        self.address = page.find('address').text()
        self.title = page.find('title').text()
        self.root = page.find('root')
        self.html_node(self.root)

    def html_node(self, node):
        tag = node.name
        attrs = get_attrs(node.find('attr'))
        self.parser.handle_starttag(tag, attrs)
        children = node.find('children')
        if children is not None:
            for child in children.list():
                self.html_node(child)
        self.parser.handle_endtag(tag)
