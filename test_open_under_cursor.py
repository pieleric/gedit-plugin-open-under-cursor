"""
Created on Jun 11, 2023

@author: Éric Piel
"""
import unittest
from open_under_cursor import get_word_around_index  # Due to Gedit not available for import, just copy-paste the code here

class TestGetWordAroundIndex(unittest.TestCase):

    def test_get_word_around_index(self):
        line = "Hello  world! This is a test line."

        # Index inside a word
        idx = 9
        expected_output = "world!"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        # Index at the beginning of a word
        idx = 8
        expected_output = "world!"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        # Index at the end of a word
        idx = 17
        expected_output = "This"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        # Index just after a word
        idx = 5
        expected_output = "Hello"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        # Index on separator (which is after another separator) => None
        idx = 6
        expected_output = None
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        # Index at the beginning of the line
        idx = 0
        expected_output = "Hello"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        # Index at the end of the line
        idx = len(line) - 1
        expected_output = "line."
        self.assertEqual(get_word_around_index(line, idx), expected_output)

    def test_no_separator(self):
        # Test case 7: Line not containing any separator
        line = "Python"
        idx = 3
        expected_output = "Python"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

    def test_one_separator(self):
        # Test case 8: Line containing only a separator at the beginning
        line = " Hello"
        idx = 0
        expected_output = None
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        idx = 1
        expected_output = "Hello"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

        idx = len(line)
        expected_output = "Hello"
        self.assertEqual(get_word_around_index(line, idx), expected_output)

    def test_fs_separators(self):
        line = "file1.doc, /var/file2.doc:3"

        idx = 2
        expected_output = "file1.doc"
        self.assertEqual(get_word_around_index(line, idx, FILENAME_SEPARATORS), expected_output)

        idx = 12
        expected_output = "/var/file2.doc"
        self.assertEqual(get_word_around_index(line, idx, FILENAME_SEPARATORS), expected_output)


if __name__ == "__main__":
    unittest.main()
