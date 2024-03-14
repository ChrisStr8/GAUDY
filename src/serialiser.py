from html.parser import HTMLParser


# Constants for serialisation
OBJECT = b'\x00'
END_OBJECT = b'\x01'
FIELD = b'\x02'
TEXT_VALUE = b'\x03'
LIST_VALUE = b'\x04'
END_LIST_VALUE = b'\x05'


class Serialiser:
    """
    Converts a HtmlPage in to a series of bytes.
    Methods tend to return self so that we can write eg. self.write(b'some data').write(b'more data').
    """

    def __init__(self):
        """
        Prepare a Serialiser
        """
        self.result = bytearray()

    def write(self, data: bytes):
        """
        Write some data to the output.
        :param data: The bytes to add
        :return: self
        """
        self.result.extend(data)
        return self

    def object(self, name: bytes):
        """
        Write an object with a name.
        :param name: The object name to add
        :return: self
        """
        self.write(OBJECT)
        self.write(name)
        return self

    def end_object(self):
        """
        Write an end-of-object sequence.
        :return: self
        """
        self.write(END_OBJECT)
        return self

    def field(self, name: bytes):
        """
        Write a field
        :param name: The field name
        :return: self
        """
        self.write(FIELD)
        self.write(name)
        return self

    def text(self, text: str):
        """
        Write a text string.
        :param text: The text tor write
        :return: self
        """

        self.write(TEXT_VALUE)
        data = text.encode('utf-8')
        # TODO: Replace control sequences in encoded text with escape sequence
        self.write(data)
        return self

    def start_list(self):
        """
        Write a list start sequence.
        :return: self
        """
        self.write(LIST_VALUE)
        return self

    def end_list(self):
        """
        Write a list end sequence.
        :return: self
        """
        self.write(END_LIST_VALUE)
        return self

    def html_node(self, node):
        """
        Write a HtmlNode.
        :param node:
        :return:
        """

        # If there is a tk object for this node, then add its type as an attribute
        tk = node.tk_object
        self.object(node.tag.encode('utf-8'))
        if tk is not None:
            self.field(b'tk_object').text(tk.widgetName)

        # Write the attribute list (list of text fields)
        if len(node.attrs) > 0:
            self.field(b'attr').start_list()
            for attr in node.attrs:
                self.field(attr[0].encode('utf-8')).text(attr[1])
            self.end_list()

        # Write the node's children (list of objects)
        if len(node.children) > 0:
            self.field(b'children').start_list()
            for child in node.children:
                self.html_node(child)
            self.end_list()

        self.end_object()
        return self

    def page(self, page):
        """
        Write an HtmlPage
        :param page: The page to be serialised
        :return: self
        """

        self.object(b'page')
        self.field(b'title').text(page.title)
        self.field(b'address').text(page.address)
        self.field(b'root').html_node(page.root)
        self.end_object()
        return self

    def get_bytes(self):
        """
        Get the encoded output.
        :return: The output from the serialiser
        """
        return bytes(self.result)


def bytes_from_html(page) -> bytes:
    """
    Serialise an HtmlPage
    :param page:
    :return:
    """
    s = Serialiser()
    s.page(page)
    return s.get_bytes()


class SerialisationError(Exception):
    """
    Thrown to indicate an error in the serialised data.
    """
    pass


# Lookout! Here be dragons!
class DeserialisedObject:
    """
    Serialised objects have a list of fields.
    """

    def __init__(self, name, fields):
        """
        Initialise the object.
        :param name: The object's name
        :param fields: The object's fields
        """
        self.name = name
        self.fields = fields

    def find(self, name):
        """
        Retrieve a field by name.
        :param name: The name of the field.
        :return: The DeserialisedField object, or None if there is no field with the given name.
        """
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def __str__(self):
        return f'({self.name}, {str([str(f) for f in self.fields])})'


class DeserialisedList:
    """
    Serialised lists contain either fields or objects.
    """

    def __init__(self, value):
        """
        Create a DeserialisedList of the given data.
        :param value: The list containing text or object values.
        """
        self.value = value

    def find(self, name):
        """
        Find a named object in the list.
        :param name: The name of the object to find.
        :return: The object, or None if not found.
        """
        for v in self.value:
            if v.name == name:
                return v
        return None

    def __str__(self):
        return str([v.name for v in self.value])


class DeserialisedField:
    """
    Serialised Fields have a name and a value, either a list, text, or an object.
    """

    def __init__(self, name, value_type, value):
        """
        Create a DeserialisedField
        :param name: The field name
        :param value_type: The type of the field.
        :param value: The field's value.
        """
        self.name = name
        self.value_type = value_type
        self.value = value

    def find(self, name):
        """
        Search in this field's value for the given name.
        :param name: The name to search for.
        :return: An object from a list value, or a field from an object value, or None if no match.
        """
        if self.value_type == LIST_VALUE or self.value_type == OBJECT:
            return self.value.find(name)
        else:
            return None

    def text(self):
        """
        Get the text from this field.
        :return: The field's text, or None if it's a list or object value.
        """
        if self.value_type == TEXT_VALUE:
            return self.value
        else:
            return None

    def list(self):
        """
        Get the list value of this field.
        :return: The field's list value, or None if it isn't a list.
        """
        if self.value_type == LIST_VALUE:
            return self.value.value
        else:
            return None

    def __str__(self):
        return f'{self.name}: {self.value}'


class Deserialiser:
    """
    Load Objects, Fields, and Values from serialised data.
    """

    def __init__(self, data):
        """
        Create a deserialiser using the given data.
        :param data: The data to convert to a page.
        """
        self.data = data
        self.index = 0

    def peek(self):
        """
        Peek at the next byte of data, without incrementing the index.
        Subsequent calls to peek without a read will return the same data.
        :return: The next byte of data.
        """
        try:
            return self.data[self.index].to_bytes()
        except IndexError as error:
            raise SerialisationError from error

    def read(self):
        """
        Retrieve the next byte of data, and increment the index.
        Repeated calls to read will retrieve the entire data.
        :return: The next byte of data.
        """
        b = self.peek()
        self.index += 1
        return b

    def read_text(self, expected: bytes):
        """
        Read a text value from data.
        Continues until a non-printing character is encountered (byte value < 0x20)
        :param expected: A prefix that is required before the text string.
        :return: The text value read as a string value.
        """

        # Check that the prefix matches the expected value
        self.expect(expected)

        # Read until a value < 0x20 (space) is encountered.
        text = bytearray()
        while self.peek()[0] == 0x0a or self.peek()[0] >= 0x20:
            text.append(self.read()[0])

        return text.decode('utf-8')

    def expect(self, value: bytes):
        """
        Raise a Serialisation error unless value matches the next bytes read from data.
        :param value: The value that must match.
        :return: self
        """

        for b in value:
            if self.peek()[0] != b:
                print('Expected: ', value)
                print(self.peek()[0], b)
                raise SerialisationError
            self.read()
        return self

    def parse_object(self):
        """
        Parse an object by reading its name and fields.
        :return: A new DeserialisedObject
        """

        # Objects begin with an OBJECT sequence and their name
        name = self.read_text(OBJECT)

        # Read the fields
        fields = list()
        while self.peek() != END_OBJECT:
            fields.append(self.parse_field())

        # Objects end with an END_OBJECT sequence
        self.expect(END_OBJECT)

        return DeserialisedObject(name, fields)

    def parse_field(self):
        """
        Parse a field by reading its name and value.
        :return: A DeserialisedField object.
        """

        # Fields begin with a FIELD sequence and their name
        field_name = self.read_text(FIELD)

        # Fields can have text, an object, or a list as their value.
        if self.peek() == TEXT_VALUE:
            # Text!
            value = self.read_text(TEXT_VALUE)
            value_type = TEXT_VALUE
        elif self.peek() == LIST_VALUE:
            # A list!
            value = self.list_value()
            value_type = LIST_VALUE
        elif self.peek() == OBJECT:
            # An object!
            value = self.parse_object()
            value_type = OBJECT
        else:
            # Something else??!!?!?!?!?!
            raise SerialisationError
        return DeserialisedField(field_name, value_type, value)

    def list_value(self):
        """
        Parse a list value.
        :return: A new DeserialisedList.
        """

        # Lists begin with a LIST_VALUE sequence.
        self.expect(LIST_VALUE)

        value = list()

        # Until we see an END_LIST_VALUE sequence, their must be more list items.
        while self.peek() != END_LIST_VALUE:
            if self.peek() == FIELD:
                # This item is a field!
                value.append(self.parse_field())
            elif self.peek() == OBJECT:
                # This item is an object!
                value.append(self.parse_object())
            else:
                # This item is not a field OR an object!!!!!?!??!?!?!???
                raise SerialisationError

        # Lists end with an END_LIST_VALUE sequence
        self.expect(END_LIST_VALUE)

        return DeserialisedList(value)


def get_attrs(encoded_attrs):
    """
    Helper method to create an HtmlNode's attributes.
    :param encoded_attrs: A DeserialisedField containing a list of DeserialisedFields.
    :return: A list of key-value pairs suitable for the GaudyParser.
    """
    attrs = list()
    if encoded_attrs is not None:
        for a in encoded_attrs.list():
            attrs.append((a.name, a.text()))
    return attrs


class HtmlDeserialiser:
    """
    Convert a sequence of bytes into an HtmlPage.
    """

    def __init__(self, parser: HTMLParser, raw: bytes):
        """
        Create a deserialiser.
        :param parser: A GaudyParser (or compatible) to control Html Construction
        :param raw: The data to be converted.
        """

        # Each page must be represented by a single encoded Object ...
        self.data = Deserialiser(raw).parse_object()
        # ... named 'page'.
        if self.data.name != 'page':
            raise SerialisationError

        # Encoded data is valid, set the page attributes.
        page = self.data
        self.parser = parser
        self.address = page.find('address').text()
        self.title = page.find('title').text()
        self.root = page.find('root')

        # Create the html nodes.
        self.html_node(self.root)

    def html_node(self, node):
        """
        Recursively create html nodes by calling self.parser.handle_{start,end}tag.
        :param node: The DeserialisedObject being fed to the parser.
        """

        # Call parser.handle_starttag to create a HtmlNode
        tag = node.name
        attrs = get_attrs(node.find('attr'))
        self.parser.handle_starttag(tag, attrs)

        # Recursively create the node's children.
        children = node.find('children')
        if children is not None:
            for child in children.list():
                self.html_node(child)

        # Call parser.handle_endtag to finish creating the node.
        # Note that void tags like <hr> might not have called handle_endtag when they were first created!
        # But when deserialising we ALWAYS call this method.
        self.parser.handle_endtag(tag)
