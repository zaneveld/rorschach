"""
Run the Game.
"""
import arcade
import os
import pandas as pd
from random import randint,choice,shuffle
from rorschach.code.deck import CardSet,EffectSet
from collections import defaultdict

# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Draft Cards"


class Draft(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #Load set data
        card_data_filepath = "../data/card_data/basic_card_set.txt"
        effect_data_filepath = "../data/effect_data/effect_data.txt"
        basic_effects = EffectSet(effect_data_filepath)
        basic_cards = CardSet(card_data_filepath,effect_library=basic_effects)
        possible_cards = basic_cards.Cards
        for c in possible_cards:
            print(c.Name,c.CardImageFilepath)
        self.PossibleCards = possible_cards
        #Set up screen variables
        self.ScreenWidth = SCREEN_WIDTH
        self.ScreenHeight = SCREEN_HEIGHT
        self.ScreenTitle = SCREEN_TITLE

        #Relative scale of cards
        self.CardScale = 0.15
        self.EnlargedCardScale = 0.25
        
        # How big are the cards?
        self.CardWidth = 825 * self.CardScale
        self.CardHeight = 1125 *self.CardScale

        # How much space do we leave as a gap between the mats?
        # Done as a ratio to the mat size.
        self.MatToCardSizeRatio = 1.25

        # How big are mats compared to cards?
        self.MatWidth = int(self.MatToCardSizeRatio * self.CardWidth)
        self.MatHeight = int(self.MatToCardSizeRatio * self.CardHeight)
        self.VerticalMarginRatio = 0.10
        self.HorizontalMarginRatio = 0.10

        #Get the starting card x position
        self.CardStartX = self.MatWidth/2 +\
          self.MatWidth * self.HorizontalMarginRatio
        
        #Get the starting card y position
        self.CardStartY = self.MatHeight/2 + \
          self.MatHeight * self.VerticalMarginRatio


        #Save the y position of the top row of cards (4 piles)
        self.TopRowY = SCREEN_HEIGHT - self.MatHeight/2 \
          - self.MatHeight * self.VerticalMarginRatio 
        
        #Save the position of the middle row of cards (7 piles)
        self.MiddleRowY = self.TopRowY - self.MatHeight \
          - self.MatHeight*self.VerticalMarginRatio

        # How far apart each pile goes
        self.XSpacing = self.MatWidth +\
          self.MatWidth * self.HorizontalMarginRatio
        
        arcade.set_background_color(arcade.color.AMAZON)
        
        #Mats for cards
        self.MatList = None

        # List of cards we are dragging with the mouse
        self.HeldCards = None

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.HeldCardsOriginalPosition = None

    def getDeckFilepath(self,deck_dir = "../data/decks/"):
        #Get a draft output file
        existing_decks = os.listdir(deck_dir)
        deck_numbers = []
        for deck in existing_decks:
            last_field =  deck.split("_")[-1].split(".")[0]
            if last_field.isdigit():
                deck_numbers.append(int(last_field))
        current_deck_number = 1
        if deck_numbers:
            current_deck_number = max(deck_numbers) + 1
        
        deck_filename = f"player_draft_{current_deck_number}.tsv" 
        deck_filepath = os.path.join(deck_dir,deck_filename)
        return deck_filepath

    def setup(self,card_dir="../data/images/cards/kingdom_of_kyberia"):
        """ Set up the game here. Call this function to restart the game. """
        
        # Sprite list with all the cards, no matter what pile they are in.
        self.CardList = arcade.SpriteList()
        
        self.DeckFile = self.getDeckFilepath()

        card_list = self.PossibleCards
        min_copies = 1
        max_copies = 10

        deck = []
        for i,card in enumerate(card_list):
            copies = randint(min_copies,max_copies)
            for c in range(copies):
                deck.append(card)
        
        #shuffle the cards
        shuffle(deck)
        

        card_image_list = [c.CardImageFilepath for c in deck]
        card_name_list = [c.Name for c in deck]

        deck = card_image_list 
        
        
        for i,card in enumerate(deck):
            card_sprite = Card(card,scale=self.CardScale)
            card_sprite.position = (self.CardStartX,self.CardStartY)
            card_sprite.name = card_name_list[i]
            self.CardList.append(card_sprite)


        # Mat sprite list
        # Sprite list with all the mats tha cards lay on.
        self.MatList = arcade.SpriteList()
        mat_color = arcade.csscolor.DARK_OLIVE_GREEN

         
        # Create the seven middle piles
        n_middle_piles = 7
        for i in range(n_middle_piles):
            pile = arcade.SpriteSolidColor(self.MatWidth, self.MatHeight,\
              mat_color)
            pile.position = self.CardStartX +\
              i * self.XSpacing,self.MiddleRowY
            
            self.MatList.append(pile)        
        
        #Deal a cards equally among middle piles
        current_mat = 0
        for i,card in enumerate(self.CardList):
            if current_mat >= len(self.MatList):
                current_mat = 0
            self.CardList[i].position = self.MatList[current_mat].position
            current_mat +=1 

        # Create the mat for the drafted cards
        drafted_card_mat = arcade.SpriteSolidColor(self.MatWidth,\
          self.MatHeight,mat_color)
       
        self.DeckMat = drafted_card_mat 

        drafted_card_mat.position = self.CardStartX, self.CardStartY
        self.MatList.append(drafted_card_mat)

        #Create a mat for discarded cards        
        discard_mat = arcade.SpriteSolidColor(self.MatWidth,\
          self.MatHeight,mat_color)

        discard_mat.position =\
          self.CardStartX + self.XSpacing, self.CardStartY
        self.DiscardMat = discard_mat

        self.MatList.append(discard_mat)
 

        #Create objects to hold our actual deck and discarded pile
        self.Deck = []
        self.Discard = []
        

        #Ensure we aren't holding any cards at first
        self.HeldCards = []
        self.HeldCardsOriginalPosition = []


        self.DeckSize = 15

        title_font_size = 20
        self.Title = arcade.Text(
            "Drag Cards to your Deck (blue) or to Discard (red)",
            self.ScreenWidth/2,
            self.TopRowY + self.MatHeight/2,
            arcade.color.BLACK,
            title_font_size,
            bold = True,
            width=self.ScreenWidth,
            align="center",
        )

        self.Report = arcade.Text(
            f"Deck:{len(self.Deck)} / {self.DeckSize} \t Discard:{len(self.Discard)}",
            self.ScreenWidth/2,
            self.TopRowY + self.MatHeight/4,
            arcade.color.BLACK,
            title_font_size,
            bold = True,
            width=self.ScreenWidth/2,
            align="center",
        )



    
    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top)        """

        # Remove, and append to the end
        self.CardList.remove(card)
        self.CardList.append(card)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.CardList)

        # Have we clicked on a card?
        if len(cards) == 0:
            #Empty held cards
            self.HeldCards = []
            self.HeldCardsOriginalPosition = []
        elif len(cards) > 0:
             
            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            primary_card.scale = self.EnlargedCardScale
            
            # All other cases, grab the face-up card we are clicking on
            self.HeldCards = [primary_card]
             
            # Save the position
            self.HeldCardsOriginalPosition = [primary_card.position]
            
            # Put on top in drawing order
            self.pull_to_top(primary_card)


    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        # Draw Title
        self.Title.draw()
        self.Report.draw()

        # Draw the mats the cards go on to
        self.MatList.draw()

        #Draw card list
        self.CardList.draw()


    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """
        # We are no longer holding cards
        if not self.HeldCards:
            return None

        # Find the closest pile, in case we are in contact 
        # with more than one

        primary_card = self.HeldCards[0]
        mat, distance =\
          arcade.get_closest_sprite(primary_card, self.MatList)
        
        #If we miss, we'll reset the card position
        reset_position = True

        # See if we are in contact with the closest pile
        if not primary_card.Active:
            #Can't move dead cards
            pass
        elif arcade.check_for_collision(primary_card, mat):

            # For each held card, move it to the pile we dropped on
            for i, dropped_card in enumerate(self.HeldCards):
                # Move cards to proper position
                dropped_card.position = mat.center_x, mat.center_y

            # Success, don't reset position of cards
            reset_position = False
            
            #Finally, see if cards should be added to the deck 
            #or discard
            if mat is self.DeckMat:
                self.Deck.append(primary_card)
                primary_card.Active = False
                print("Current cards:",[c.name+"\n" for c in self.Deck])
                self.Report.text = f"Deck:{len(self.Deck)} / {self.DeckSize} \t Discard:{len(self.Discard)}"
                if len(self.Deck) == self.DeckSize:
                    self.writeDeckToFile(self.DeckFile)
                    self.writeDeckToFile("../data/decks/latest_player_draft.tsv")
                    exit()
            elif mat is self.DiscardMat:
                self.Discard.append(primary_card)
                primary_card.Active = False
                print("Discarded cards:",[c.name+"\n" for c in self.Discard])
                self.Report.text = f"Deck:{len(self.Deck)} / {self.DeckSize} \t Discard:{len(self.Discard)}"
        
        if reset_position:
            # Where-ever we were dropped, it wasn't valid. 
            # Reset the each card's position to its original spot.
            for i, returned_card in enumerate(self.HeldCards):
                returned_card.position = self.HeldCardsOriginalPosition[i]

        for c in self.HeldCards:
            c.scale = self.CardScale

        self.HeldCards = []
        self.HeldCardsOriginalPosition = []
        
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
         
        # If we are holding cards, move them with the mouse
        for card in self.HeldCards:
            card.center_x = x
            card.center_y = y

    def writeDeckToFile(self,filepath):
        """Collate cards in deck and write to deckfile"""
        row_list = []
        
        deck_as_dict = defaultdict(int)
        for card in self.Deck:
            deck_as_dict[card.name] += 1

        for card,copies in deck_as_dict.items():
            row_list.append([card,copies])

        deck_df = pd.DataFrame(row_list,\
          columns=['card_name', 'copies'])

        deck_df = deck_df.set_index('card_name')
        
        deck_df.to_csv(filepath,sep="\t")

class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, card_image_fp, scale=1):
        """ Card constructor """

        self.CardImage = card_image_fp
        self.Active = True

        # Call the parent
        super().__init__(self.CardImage, scale, hit_box_algorithm="None")






def main():
    """ Main function """
    window = Draft()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
