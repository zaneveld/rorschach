import unittest
from pandas.testing import assert_frame_equal
from rorschach.code.deck import Deck
from collections import deque

class TestDeck(unittest.TestCase):

    def setUp(self):
        """Set up some example associations for testing"""
        self.SimpleDeck = Deck([1,2,3,4,5,6])

    def test_Deck__init__method_functions_with_list_input(self):
        """Deck object initializes with a simple list"""
        observed = len(self.SimpleDeck)
        expected = 6
        self.assertEqual(observed,expected)

    def test_Deck__init__method_functions_with_list_input(self):
        """Deck object initializes with a simple list"""
        observed = len(self.SimpleDeck)
        expected = 6
        self.assertEqual(observed,expected)


    def test_draw_method_can_draw_a_single_card(self):
        """Deck.draw draws multiple cards if requested"""
        observed = self.SimpleDeck.draw(1)
        expected = [1]
        self.assertEqual(observed,expected)


    def test_draw_can_draw_multiple_cards(self):
        """Deck.draw draws multiple cards if requested"""
        observed = self.SimpleDeck.draw(3)
        expected = [1,2,3]
        self.assertEqual(observed,expected)

    def test_draw_removes_cards_from_deck_when_drawn(self):
        """Deck.draw removes cards from Deck when drawn"""
        drawn_cards = self.SimpleDeck.draw(4)
        observed = self.SimpleDeck.Cards
        expected = deque([5,6])
        self.assertEqual(observed,expected)

    def test_draw_multiple_cards_into_empty_deck(self):
        """Deck.draw draws multiple cards if requested"""
        observed = self.SimpleDeck.draw(7)
        expected = [1,2,3,4,5,6]
        self.assertEqual(observed,expected)

    def test_shuffle(self):
        """Deck.shuffle shuffles cards"""
        n_times_cards_changed_order = 0
        n_trials = 10
        for i in range(n_trials):
            old_order = list(self.SimpleDeck.Cards)
            self.SimpleDeck.shuffle()
            new_order = list(self.SimpleDeck.Cards)
            if old_order != new_order:
                n_times_cards_changed_order +=1

        #Allow for very rare cases where you shuffle into same order
        self.assertTrue(n_times_cards_changed_order >= n_trials - 1)

    def test_toDeckList(self):
        """toDecklist converts a Deck into a decklist"""
        pass  
        
#Run the tests
unittest.main()
