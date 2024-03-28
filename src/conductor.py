from context import Context
import serialiser
import dom

import socket
import select
import re

import tkinter as tk
import tkinter.ttk as ttk

from messageProtocol import MessageProtocol
from messageType import *


class Conductor(Context):
    """
    Conductor class loads pages from the internet and sends them to collaborators.
    """

    def __init__(self, cid, home):
        """
        Create a Conductor. It will automatically load the homepage.
        :param cid: The Context Name
        """

        # Call Context initialiser to create window
        super().__init__(cid)

        # Setup user interface
        self.address_bar = None
        ui = self.make_ui_frame()

        # Setup navigation history
        self.pages = [None]
        self.page_history = list()
        self.back_history = list()
        self.collaborators = list()
        self.current_page_data = None

        # Navigate to the homepage
        self.go_to_page(home)

        # Prepare to accept collaborators.
        self.server_socket = socket.create_server(('0.0.0.0', 10000))
        self.server_socket.setblocking(False)
        self.window.after(10, lambda: self.check_network())

        # Start the application
        self.window.mainloop()

    def check_network(self):
        """
        Accept connections from collaborators and add them to a list to be updated when the page changes.
        """

        # Check for collaborators waiting to connect
        ready = select.select([self.server_socket], [], [], 0)

        while self.server_socket in ready[0]:
            # Accept a new collaborator
            connection, address = self.server_socket.accept()
            connection.setblocking(False)
            collaborator = MessageProtocol(connection, self.cid)
            self.collaborators.append((collaborator, address, connection))

            # Send current page data to the collaborator
            collaborator.navigate(self.current_page().address)
            collaborator.pagedata(self.current_page_data)

            # Check for another collaborator
            ready = select.select([self.server_socket], [], [], 0)

        sockets = [c[2] for c in self.collaborators]
        if len(sockets) == 0:
            ready = ([], [], [])
        else:
            ready = select.select([c[2] for c in self.collaborators], [], [], 0)
        for c in self.collaborators:
            if c[2] in ready[0]:
                print('ready')
                collaborator = c[0]
                messages = collaborator.receive()
                for m in messages:
                    if m.message_type == MESSAGE_DISCONNECTED:
                        collaborator.active = False
                    if m.message_type == MESSAGE_INVALID:
                        collaborator.active = False
                    elif m.message_type == MESSAGE_TIMEOUT:
                        collaborator.active = False
                    elif m.message_type == MESSAGE_NAVIGATION:
                        self.go(m.data.decode('utf-8'))
                    elif m.message_type == MESSAGE_PAGEDATA:
                        collaborator.active = False
                    else:
                        collaborator.active = False

        for c in self.collaborators:
            if not c[0].active:
                self.collaborators.remove(c)

        # Schedule next check after another second.
        self.window.after(1000, lambda: self.check_network())

    def current_page(self):
        """
        Get the currently visible page
        :return: The current page
        """
        return self.pages[self.focused_page]

    def make_ui_frame(self):
        """
        Setup user interface for the Conductor. Conductor user interface has navigation buttons (back/forward),
        address bar, 'GO!' button, and 'Collaborate' button
        """

        # Create Frame to contain UI
        ui_frame = ttk.Frame(self.root)
        ui_frame.grid(column=0, row=0, sticky=tk.EW)

        # Create Navigation Buttons (back and forward)
        nav_section = ttk.Frame(ui_frame)
        ttk.Button(nav_section, text='Back', style='Gaudy.TButton', command=self.back).grid(column=0, row=1,
                                                                                            sticky=tk.W)
        ttk.Button(nav_section, text='Forward', style='Gaudy.TButton', command=self.forward).grid(column=1, row=1,
                                                                                                  sticky=tk.E)

        # Create address entry
        address = tk.StringVar()
        address_bar = ttk.Entry(ui_frame, textvariable=address)

        # Create 'Go!' button
        go_to_button = ttk.Button(ui_frame, text='Go!', command=lambda: self.go(address.get()),
                                  style='GaudyGo.TButton')

        # Create collaborate button
        collaborate_button = ttk.Button(ui_frame, text='Collaborate',
                                        command=lambda: self.display_collaboration_options(), style='Gaudy.TButton')

        # Layout components
        ui_frame.grid_columnconfigure(1, weight=1)
        nav_section.grid(row=0, column=0, sticky=tk.W)
        address_bar.grid(row=0, column=1, sticky=tk.NSEW)
        go_to_button.grid(row=0, column=2, sticky=tk.E)
        collaborate_button.grid(row=0, column=3, sticky=tk.E)

        # Setup key bindings:
        #   CTRL-L activates the address bar
        #   RETURN in the address bar is equivalent to pressing 'Go!'
        address_bar.bind('<Return>', lambda e: go_to_button.invoke())
        self.window.bind('<Control-l>', lambda e: address_bar.focus())

        # Have the address bar grab focus
        address_bar.focus()
        self.address_bar = address_bar

        return ui_frame

    def go(self, url):
        """
        Update the navigation history and load a new page.
        :param url: The URL of the page to load
        """
        self.page_history.append((self.current_page().address, self.current_page_data))
        self.go_to_page(url)

    def finish_going(self):
        """
        Perform miscellaneous tasks required after a page has been loaded by go_to_page() or revisit().

        """

        # Set the window title.
        self.window.title(self.current_page().title)

        self.current_page().render()

        # Make links clickable
        self.current_page().renderer.bind_links(self)
        # Find all '<a>' tags
        for anchor in self.current_page().find_nodes('a'):
            children = list()
            # Get the 'data' nodes from the anchor
            anchor.find_nodes(children, 'data')
            for child in children:
                # Bind the primary mouse click action on each label to activate the link.
                # This whole expression is wrapped in a lambda to force the binding of the child variable.
                # Without this ALL links on the page will go to the same place.
                # This is because the child reference is changed, with the nested lambda using the same binding.
                # If you know a better way to do this, please tell Stuart :)
                (lambda c=child, a=anchor: c.tk_object.bind("<Button-1>",
                                                            lambda event: self.go(
                                                                self.make_path(a.get_attr('href')))))()

        # Send the page data to each collaborator
        for collaborator in self.collaborators:
            try:
                collaborator[0].pagedata(self.current_page_data)
            except IOError:
                collaborator[0].disconnect()

    def make_path(self, url):
        addr = self.current_page().address
        proto, _, path = addr.partition('://')

        # Ignore any fragment
        if url[0] == '#':
            # Fragment relative to current page - reload the page
            return addr

        # Strip fragment
        frag_pos = url.find('#')
        if frag_pos != -1:
            url = url[0:frag_pos]

        if re.match(r'\w*:.*', url):
            # Full url
            return url
        elif url[0] == '/':
            # Absolute path
            before, sep, after = path.partition('/')
            return proto + '://' + before + url
        else:
            # Relative path
            before, sep, after = path.rpartition('/')
            return proto + '://' + before + '/' + url

    def go_to_page(self, url):
        """
        Load a page from the internet.
        :param url: The url of the page to load.
        """

        # Clear the forward navigation history
        self.back_history = list()

        # Set the url in the address bar
        # Needed for non-user initiated navigation (e.g. homepage loaded).
        self.set_address(url)

        # Send a navigation message to each collaborator
        for collaborator in self.collaborators:
            try:
                collaborator[0].navigate(url)
            except IOError:
                collaborator[0].disconnect()

        try:
            # Destroy previous page (if any)
            if self.current_page() is not None:
                self.current_page().delete()

            # Create frame to contain page components
            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)

            # Load the page!
            self.pages[self.focused_page] = dom.create_page_from_url(url, page_frame)

            # Save serialised page data
            self.current_page_data = serialiser.bytes_from_html(self.current_page())

            # Finalise loading
            self.finish_going()

        except ValueError as e:
            print(e)

    def revisit(self, page_data):
        """
        Reload a previously visited page
        :param page_data: Serialised page data
        """

        # Set the address bar to the page's url
        self.set_address(page_data[0])

        # Send a navigation message to each collaborator
        for collaborator in self.collaborators:
            try:
                collaborator[0].navigate(page_data[0])
            except IOError:
                collaborator[0].disconnect()

        try:
            # Destroy the current page (if any)
            if self.current_page() is not None:
                self.current_page().delete()

            # Create frame to contain page components
            page_frame = ttk.Frame(self.root)
            page_frame.grid(row=1, column=0, sticky=tk.NSEW)

            # Rebuild the page from serialised data
            self.pages[self.focused_page] = dom.deserialise_page(page_data[1], page_frame)
            self.current_page_data = page_data[1]

            # Finalise loading
            self.finish_going()

        except ValueError as e:
            print(e)

    def back(self):
        """
        Navigate backward through navigation history.
        """
        if len(self.page_history) > 0:
            # Get previous page
            prev = self.page_history.pop()

            # Store current page for future 'forward' navigation
            self.back_history.append((self.current_page().address, self.current_page_data))

            # Load the previous page
            self.revisit(prev)

    def forward(self):
        """
        Navigate forward through navigation history.
        """
        if len(self.back_history) > 0:
            # Get next page
            prev = self.back_history.pop()

            # Store current page for future 'back' navigation
            self.page_history.append((self.current_page().address, self.current_page_data))

            # Load the next page
            self.revisit(prev)

    def display_collaboration_options(self):
        """
        Display a dialogue with list of connected collaborators.
        """

        # Create window for the dialogue
        collab_menu = tk.Toplevel(self.window)
        collab_menu.resizable(False, False)
        collab_menu.title(self.cid + ': Collaborators')
        collab_menu.grid()

        # Create frame to contain labels
        frame = ttk.Frame(collab_menu)
        frame.grid(sticky=tk.NSEW)

        # Label so that the window isn't totally empty when no-one is connected
        ttk.Label(frame, text='Connected collaborators:').grid()

        # Label with the name (host/ip + port) of each collaborator
        for collaborator in self.collaborators:
            label = ttk.Label(frame, text=collaborator[0].remote_name + ' ' + str(collaborator[1]))
            label.grid()
