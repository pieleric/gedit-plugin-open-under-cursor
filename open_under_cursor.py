# gedit plugin to automatically open in a new tab the file based on the name under the cursor.
# This is triggered with Ctrl+Shift+O
# This is a similar feature as in vim the "gf" function.
# If there is a text selection, it's used as-is for the filename.
# Otherwise, the file name is guessed as the word around the cursor.

import os

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gedit', '3.0')
from gi.repository import GObject, Gtk, Gedit, Gdk, Gio

class OpenSelectedFilePluginApp(GObject.Object, Gedit.AppActivatable):
    app = GObject.property(type=Gedit.App)
    __gtype_name__ = "OpenSelectedFilePluginApp"

    def __init__(self):
        GObject.Object.__init__(self)
        self.menu_ext = None
        self.menu_item = None

    def do_activate(self):
        self.app.set_accels_for_action("win.open-under-cursor", ["<Ctrl><Shift>O"])

    def do_deactivate(self):
        self.app.set_accels_for_action("win.open-under-cursor", ())

class OpenSelectedFilePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "OpenSelectedFilePlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        # Create an action
        action = Gio.SimpleAction(name="open-under-cursor")#, label="Open File Under Cursor", tooltip="Display the path of the current document")
        action.connect("activate", self.open_file)

        # Add the action to the Gedit window
        self.window.add_action(action)

        # Set the accelerator for the action
#        self.window.set_accels_for_action("win.open-under-cursor", ["<Ctrl><Shift>O"])

    def do_deactivate(self):
        # Remove the action from the Gedit window
        self.window.remove_action("open-under-cursor")

        # Remove the accelerator for the action
#        self.window.unset_accels_for_action("win.open-under-cursor")

    def open_file(self, action, data):
        # Get the current text selection
        selection = self.get_selected_text()
        
        if not selection:
            # If selection is empty, get the word around the cursor
            selection = self.get_word_around_cursor()

        print(f"selection: {selection}")
        if selection:
            # Check if the file exists
            # TODO: don't use the current working dir from the process, but the path from current document
#            selection_path = os.path.abspath(selection)
            selection_path = self.get_abs_path_from_current_doc(selection)
            print(f"full path: {selection_path}")

            # Check if the file exists
            if os.path.exists(selection_path):
                # Open the file in a new tab
                location = Gio.file_new_for_path(selection_path)
                self.window.create_tab_from_location(location, None, 0, 0, False, True)
            else:
                # A better, but still subtile way to indicate the shortcut was received, but the filename doesn't match anything?
                print(f"Couldn't find file '{selection_path}', not opening it")


    def get_abs_path_from_current_doc(self, path: str) -> str:
        """
        return an absolute path corresponding to the current path.
        Similar to os.path.abspath(), but instead of use the current working directory (of the process),
        use the directory of the current document.
        """
        if os.path.isabs(path):
            # Just take it as is
            return path
        else:
            doc = self.window.get_active_document()

            if not doc: # Shouldn't happen
                return path
            file_uri = doc.get_uri_for_display()  # Typically, just the path, but could start with "file://" ??
            
            print(f"current uri = {file_uri}")
            file_path = doc.get_uri_for_display().replace('file://', '')  # Remove the file:// in case it's there
            base = os.path.dirname(file_path)
            return os.path.join(base, path)

    def get_selected_text(self):

        # Get the current active document
        doc = self.window.get_active_document()
        # Get the selection bounds
        bounds = doc.get_selection_bounds()

        if bounds:
            # Get the selected text
            start_iter, end_iter = bounds
            return doc.get_slice(start_iter, end_iter, True)

        return None

    def get_word_around_cursor(self) -> str:
        """
        return the word (filename) that is just after or around the cursor
        return None if no word
        """
        # Get the current active document
        doc = self.window.get_active_document()
        # Get the current cursor position
        cursor = doc.get_iter_at_mark(doc.get_insert())
        cursor_pos = cursor.get_line_offset()

        # Get the current line
        start_iter = cursor.copy()
        start_iter.set_line_offset(0)
        end_iter = start_iter.copy()
        if not end_iter.ends_line():
            end_iter.forward_to_line_end()
        line_str = doc.get_text(start_iter, end_iter, True)
        print(f"cursor at {cursor_pos}, line: {line_str}")
        # Get the word boundaries around the cursor
#        start_iter, end_iter = doc.get_word_at_cursor(cursor)

#        if start_iter and end_iter:
#            # Get the word text
#            return doc.get_text(start_iter, end_iter, True)
        word = self.get_word_around_index(line_str, cursor_pos)
        print(f"found word: {word}")
        if word == "":
            return None
        
        return word

    def get_word_around_index(self, line, idx):
        # TODO: use regex, to match a set of characters, not just space (see "ifsname" from vim): " \t,"
        before_idx = line.rfind(" ", 0, idx) + 1 # returns -1 if not found => idx at 0
        after_idx = line.find(" ", idx)  # returns -1 if not found => idx at the end
        if after_idx == -1:
            after_idx = None  # means "until the end"
        print(f"found indices {before_idx} -> {after_idx}")
        return line[before_idx:after_idx]

