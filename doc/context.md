# Context API

`context.py` contains the `Context`, `Conductor` and `Collaborator` classes.

## Class `Context`

`Context` serves as the parent to `Conductor` and `Collaborator`, and handles the shared behavior, such as initialising styles and creating the top-level window.

### Properties
- `cid`
  - The name of the context
- `pages`
  - List of pages visible
  - Only a single page is supported at present
- `window`
  - Top-level Tk window
- `root`
  - Root Tk frame
- `focused_page`
  - Index into `pages` of currently visible page

### Methods
- `Context(cid)`
  - Create a new context with the provided id.
  - This will create a new Tk window, and a root ttk.Frame that will fill it.
- `make_ui_frame()`
  - Create the user interface widgets for this context.
- `make_page_frame()`
  - Has no effect

## Class `Collaborator`

`Collaborator` is a specialisation of `Context` - it is not yet implemented.

## Class `Conductor`

`Conductor` is a specialisation of `Context` for users who will browse by themselves or host a shared session.

### Methods
- `Conductor(cid)`
  - Creates a new `Conductor` with the given id.
- `make_ui_frame()`
  - Creates the user interface components for Conductor.
  - These are navigation buttons (forward/back), a text field to enter the page address, a button to 'Go!', and a button to Collaborate.
- `go_to_page(url)`
  - Loads the page at the given url and displays it.
  - Uses the DOM API
  - Triggered by pressing the 'Go!' button (or pressing 'Return' when focussed on the address input).
- `display_collaboration_options()`
  - Open a dialogue describing collaboration settings 
  - Triggered by pressing the 'Collaborate' button
