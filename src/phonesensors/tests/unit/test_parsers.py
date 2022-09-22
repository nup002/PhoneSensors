import unittest

class TestBaseParser(unittest.TestCase):
    def test_json(self):
        """
        Test that a call of JSON-formatted string returns a list of dictionaries.
        """
        in_string = "{\"a\"=1}\n{\"b\"=2}"
