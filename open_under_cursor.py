"""
Created on Jun 06, 2023

@author: Éric Piel
"""
# gedit plugin to automatically open in a new tab the file based on the name under the cursor.
# This is triggered with Ctrl+Shift+O
# This is a similar feature as in vim the "gf" function.
# If there is a text selection, it's used as-is for the filename.
# Otherwise, the file name is guessed as the word around the cursor.

import os
import re
from typing import Optional

import gi
gi.require_version('Gedit', '3.0')
from gi.repository import GObject, Gedit, Gio

# Any separator for the filenames, encoded as a regex.
# These are not the "forbidden" characters
# from a filename according to the OS. These are just the characters that are
# more likely to be before or after a filename than in the filename.
FILENAME_SEPARATORS = r'\s\",:()[\]{}'


# TODO: change to take the regex of a *word* instead of a separator? This could allow
# to search for words that contain a ., but which don't end with a .
def get_word_around_index(line: str, idx: int, separators: str=r"\s") -> Optional[str]:
    """
    Get the word around the specified index in a given line.
    It return the word which has a character on the given idx, as well as for which
    the last character is just before idx. For instance, " The", with indices 1,2,3,4
    will return "The".

    Args:
        line: The line of text to extract the word from.
        idx (0 .. len(line)): The index to locate the word around.
        separators: a regex pattern defining the set of characters that separate words.
        Defaults to whitespaces.

    Returns:
        str: The word found around the specified index, or None if no word is found.

    Raises:
        ValueError: If the specified index is out of range.
    """
    if idx > len(line):
        raise ValueError(f"idx {idx} > than line length of {len(line)}.")

    re_word = f"[^{separators}]+"

    # Go through every every word, until it finds the one spanning over the index.
    for m in re.finditer(re_word, line):
        if m.start() <= idx <= m.end():
            # we are just on the right word
            return m.group()
        elif m.start() > idx:
            # Too far, not need to search more
            break

    return None


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
        action = Gio.SimpleAction(name="open-under-cursor")  # , label="Open File Under Cursor", tooltip="Display the path of the current document")
        action.connect("activate", self.open_file)

        # Add the action to the Gedit window
        self.window.add_action(action)

    def do_deactivate(self):
        # Remove the action from the Gedit window
        self.window.remove_action("open-under-cursor")

    def open_file(self, action, data):
        # Get the current text selection
        selection = self.get_selected_text()

        if not selection:
            # If selection is empty, get the word around the cursor
            selection = self.get_word_around_cursor()

        # print(f"selection: {selection}")
        if selection:
            # TODO: if the selection starts with http:// -> open in a browser
            # Check if the file exists
            selection_path = self.get_abs_path_from_current_doc(selection)
            # print(f"full path: {selection_path}")

            # Check if the file exists
            if os.path.exists(selection_path):
                # Open the file in a new tab
                location = Gio.file_new_for_path(selection_path)
                # TODO: if URI is already opened, jump to the tab, instead of opening another one
                self.window.create_tab_from_location(location, None, 0, 0, False, True)  # location, encoding, line, column, create, jump_to
            else:
                # A better, but still subtle way to indicate the shortcut was received, but the filename doesn't match anything?
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

            if not doc:  # Shouldn't happen
                return path
            file_uri = doc.get_uri_for_display()  # Typically, just the path, but could start with "file://" ??

            # print(f"current uri = {file_uri}")
            file_path = file_uri.replace('file://', '')  # Remove the file:// in case it's there
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
        # print(f"cursor at {cursor_pos}, line: {line_str}")

        word = get_word_around_index(line_str, cursor_pos, FILENAME_SEPARATORS)
        # print(f"found word: {word}")
        # Trick: usually a filename doesn't end with a . (but they can contain some)
        # so drop the last ".".
        if len(word) > 1 and word[-1] == ".":
            word = word[:-1]

        return word
