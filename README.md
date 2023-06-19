gedit plugin to automatically open in a new tab the file based on the name under the cursor.

Usage
-----

Either place the cursor on a filename, or select the whole filename, and then
press Ctrl+Shift+O. If a file with the name is found, it is opened in a new tab.

This is a similar feature as in vim the "gf" function.

Note that when no selection is present, the filename is guessed as the word
around the cursor, based on common delimiters. If this doesn't work, select
explicitly the name of the file.
File names starting with a / are considered absolute, and are opened as-is. Otherwise,
the filename is considered "relative", and is searched relative to the directory
containing the current file.

As a special case, If the name starts with http://, https:// or ftp://, it is
opened in a webbrowser.

Installation
------------
To install, type::

    mkdir -p ~/.local/share/gedit/plugins/
    cp open_under_cursor.py open_under_cursor.plugin ~/.local/share/gedit/plugins/
    
Alternatively, if you want to easily modify the code in the git repository:

    ln -s $(readlink -m open_under_cursor.py) ~/.local/share/gedit/plugins/
    ln -s $(readlink -m open_under_cursor.plugin) ~/.local/share/gedit/plugins/

Development
-----------
Tested on gedit version 3.36.
For the API documentation, see https://developer-old.gnome.org/gedit/3.30/ .
