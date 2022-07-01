import unittest
from pandas.testing import assert_frame_equal
from rorschach.code.get_card_portrait import dir_from_location_name,filename_from_card_name, get_prompt

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


    def test_filename_from_card_name(self): 
        """filename_from_card_name functions on a complex name"""
        location = "Ka'vanaha'a-Bahia"
        card_name = "O'Malley tha' Smasha'"
        number = "0"
        extension = ".png"
        observed = filename_from_card_name(card_name,location,number=number)
        expected = "kavanahaa-bahia__omalley_tha_smasha__0.png"
        self.assertEqual(observed,expected)


    def test_get_prompt(self):
        """get_prompt functions with just a card name"""
        expected = "crungus"
        observed = get_prompt("crungus")
        self.assertEqual(observed,expected)

        
#Run the tests
unittest.main()
