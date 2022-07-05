from random import shuffle,choice
from collections import deque,defaultdict
import pandas as pd
import  ast
from rorschach.code.make_card_image import make_game_card
from rorschach.code.get_card_portrait import dir_from_location_name,filename_from_card_name,\
  get_location_dir
import os
from os import listdir
from rorschach.code.effect import EffectSet,Effect,DealDamage,Draw,GainManaCrystals,Heal,DiscardRandom
from rorschach.code.player import Player
from card import Card,Spell,Creature,CardSet

class Deck(object):

    def __len__(self):
        """Return number of cards in Deck"""
        return(len(self.Cards))

    def __init__(self,cards = None):
        """Initialize a deck of cards
        cards -- a list or deque of Card objects
        The leftmost side of the deque is the 'top' 
        """ 

        self.Cards = deque([])
        if cards:
            self.Cards.extend(cards)

    def __iter__(self):
        """Iterate directly over self.Cards"""
        for c in self.Cards:
            yield c

    def draw(self,n_cards=1):
        drawn_cards = []
        for n in range(n_cards):
             if self.Cards:
                curr_card = self.Cards.popleft()
                drawn_cards.append(curr_card)
             else:
                print("Out of Cards!")
        return drawn_cards

    def shuffle(self):
        shuffle(self.Cards)

    def toDeckList(self):
        cards = defaultdict(int)
        for card in self.Cards:
            cards[str(card)] +=1
        return "\n".join(["\t".join([str(k),str(cards[k])]) for k in cards.keys()])

def load_deck(deck_path,card_library):
    """Load a deck
    deck_path -- path to a .tsv file for the deck

    deck .tsv files should have card_name\tcopies
    all card names *must* be in the card_data file
    """
    print(f"Loading deck from path {deck_path}")
    decklist = pd.read_csv(deck_path,"\t")
    card_names=list(decklist["card_name"])
    decklist.set_index("card_name",inplace=True,drop=False)
    decklist.dropna(axis=0,how="all", inplace=True)
    decklist.dropna(axis=1,how="all", inplace=True)
    print("About to build deck from decklist:",decklist)
    deck = []
    print("Unique cards in decklist:",card_names)
    for card_name in card_names:
        copies = decklist.loc[card_name,"copies"]
        print(f"Making {card_name} x{copies}")
        this_card = card_library.makeCards([card_name],copies)
        print("Current card:",this_card)
        deck.extend(this_card)
        print("Deck:",deck)
    print("Loaded a deck with these cards:",deck)
    return deck

if __name__ == "__main__":
    #Demo how to set up a game

    #Load set data
    card_data_filepath = "../data/card_data/basic_card_set.txt"
    effect_data_filepath = "../data/effect_data/effect_data.txt"
    basic_effects = EffectSet(effect_data_filepath)
    basic_cards = CardSet(card_data_filepath,effect_library=basic_effects)

    #Load decks
    player_1_name = "Player"
    player_1_deck_path = "../data/decks/latest_player_draft.tsv"
    player_1_deck_cards = load_deck(player_1_deck_path,card_library=basic_cards)
    player_1_deck = Deck(player_1_deck_cards)
    print(f"{player_1_name} decklist:", player_1_deck.toDeckList())
    player_1 = Player(name=player_1_name,deck=player_1_deck)

    player_2_name = "King Kyber"
    player_2_deck_path = "../data/decks/King_Kyber_starter_deck.txt"
    #player_2_name = "Bloodtusk"
    #player_2_deck_path = "../data/decks/Bloodtusk_starter_deck.txt"
    player_2_deck_cards = load_deck(player_2_deck_path,card_library=basic_cards)
    player_2_deck = Deck(player_2_deck_cards)
    print(f"{player_2_name} decklist:", player_2_deck.toDeckList()) 
    player_2 = Player(name = player_2_name,deck=player_2_deck)
   
    print("ABOUT TO RUN GAME!!!!!") 
    #Run game
    game = Game(player_1,player_2)
    game.runGame() 
