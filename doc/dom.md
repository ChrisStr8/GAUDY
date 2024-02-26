# Document Object Model API

`dom.py` contains classes for manipulating the Document Object Model (DOM) and loading HTML documents from the internet.

## Class `HtmlNode`

`HtmlNode` represents an HTML Tag (such as `<p>`) or text embedded in an HTML Document.

### Properties

- `parent`
  - The containing tag - this will be `None` for the top-level `html` tag.
- `children`
  - List of nodes contained by this node.
- `tag`
  - Name of the tag - embedded text is represented with a `data` tag.
- `attrs`
  - List of `(string,string)` tuples representing additional attributes assigned to a tag (eg. `class` or `id`).
  - `<data>` tags have the `text` attribute set to the text they contain.

### Methods

- `HtmlNode(parent, tag, attrs)`
  - Create a new node with specified properties.
  - `children` is set to an empty list.
- `add_child(child)`
  - Adds a child node to the list of children.
- `find_nodes(result, selector)`
  - Recursively searches this node and its children for nodes that match the `selector`.
  - `selector` is the name of the tag to match.
  - Matching nodes are added to the `result` list.
- `get_attr(attr)`
  - Searches `attrs` for the named attribute.
  - Returns `None` if no such attribute is found.
- `delete()`
  - Nodes contain a reference to their parent, which can cause Python's reference counting garbage collection to believe that they are still reachable when they ought to be freed.
  - Calling `delete` recursively removes these references, allowing the garbage collector to do its job properly.

## Class `GaudyParser`

`GaudyParser` is a specialisation of the builtin `html.HTMLParser`.
You probably shouldn't need to use it directly.

### Properties

- `root`
  - Top level `html` node
- `parent`
  - Current parent node

### Methods

- `handle_starttag(tag, attrs)`
  - Creates a new HtmlNode with given attributes.
  - Sets `parent` to the new tag.
- `handle_endtag(tag)`
  - Sets `parent` to `parent`'s `parent`
- `handle_data(data)`
  - Create a new `data` tag
  - Has no effect if `data` is empty or entirely composed of whitespace.

## Class `HtmlPage`

`HtmlPage` represents the entire Html Document.

### Properties

- `root`
  - Top-level `html` node.
- `address`
  - The Url associated with the page.
- `Title`
  - The page title.

### Methods

- `HtmlPage(url)`
  - Access the given url (using `urllib.request.urlopen`) and create a page from it.
  - Url is assumed to represent a Html Document.
  - Document is assumed to be encoded in utf-8.
  - Document is assumed to contain no implicitly closed tags, or other confusing HTML code.
  - If the document has no `title` tag, then the page title will be set to the url.
- `find_nodes(selector)`
  - Returns a list of nodes matching `selector`.
  - `selector` specifies the tag to match.
- `find_children(*selectors)`
  - Uses a chain of selectors for more precise lookup than `find_nodes`.
- `delete()`
  - Calls the `delete` method on the `root` node.
