import unittest
from pandas.testing import assert_frame_equal
from rorschach.code.get_card_portrait import dir_from_location_name

class TestGetCardPortrait(unittest.TestCase):
    def setUp(self):
        """Set up some example associations for testing"""
        pass

    def test_dir_from_location_name_replaces_spaces(self):
        """dir_from_location_name replaces spaces"""
        location = "howling mines"
        observed = dir_from_location_name(location) 
        expected = "howling_mines"
        self.assertEqual(observed,expected)

    def test_dir_from_location_name_lowercases(self):
        """dir_from_location_name uses lowercase"""
        location = "The Caves of KelThelar"
        observed = dir_from_location_name(location)
        expected = "the_caves_of_kelthelar"
        self.assertEqual(observed,expected)

    def test_dir_from_location_name_removes_bad_chars(self):
        """dir_from_location_name filters out bad chars from dirname"""
        location = "Ka'vanaha'a-Bahia"
        observed = dir_from_location_name(location)
        expected = "kavanahaa-bahia"
        self.assertEqual(observed,expected)
 
#Run the tests
unittest.main()
