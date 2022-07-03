"""
Run the Game.
"""
import arcade
import os
import pandas as pd
from random import randint,choice,shuffle
from collections import defaultdict
from rorschach.code.deck import CardSet,EffectSet
from rorschach.code.player import Player

# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Draft Cards"


class InstructionView(arcade.View):
    """Show Instructions Screen"""

    def setup(self):
        """Set up the instruction screen"""
        pass

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        arcade.draw_text("Instructions Screen", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        map_view = MapView()
        map_view.setup()
        self.window.show_view(map_view)

class MapView(arcade.View):
    def setup(self):
        """Set up the Map screen"""
        pass

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        arcade.draw_text("Map Screen", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance (skips to GameView for testing)", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        #draft_view = DraftView()
        #draft_view.setup()
        #self.window.show_view(draft_view)
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)



class GameView(arcade.View):
    """Show the consequences of game actions"""
    def init(self):
        super().__init__()

    def setup(self,draft=None):
        """Set up the Game screen"""
 
        #For now cheat and extract all necessary information
        #from the Draft object
        #if not draft:
        #    raise NotImplementedError("Direct access to GameView without a preceding draft isn't yet supported")
        #self.DraftView = draft
        #Steal all the data!
        #self.PlayerDeck = self.DraftView.Deck
        
        # Mat sprite list
        # Sprite list with all the mats tha cards lay on.

        self.Spacing = SpaceManager(n_columns = 10, n_rows = 6)


        self.PlayerBoard = arcade.SpriteList()
        self.draw_mat_row(self.Spacing.Row[1],sprite_list=self.PlayerBoard)
        
        self.LocationBoard = arcade.SpriteList()
        self.draw_mat_row(self.Spacing.Row[2],sprite_list=self.LocationBoard)
             
        self.OpponentBoard = arcade.SpriteList()
        self.draw_mat_row(self.Spacing.Row[3],sprite_list = self.OpponentBoard)

    def draw_mat_row(self,row_center_y,sprite_list, n_columns=10,mat_color = arcade.csscolor.DARK_OLIVE_GREEN):
        """Draw a mat row"""

        for i in range(n_columns):
            pile = arcade.SpriteSolidColor(self.Spacing.MatWidth, self.Spacing.MatHeight,\
              mat_color)
            pile.position = (self.Spacing.Column[i],row_center_y)
            print(f"Current pile position (column {i}):",pile.position)
            sprite_list.append(pile)
 
  
    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """ Draw this view """
        self.clear()

        self.PlayerBoard.draw()
        self.LocationBoard.draw()
        self.OpponentBoard.draw()

        arcade.draw_text("Game Screen", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        map_view = MapView()
        map_view.setup()
        self.window.show_view(map_view)



class SpaceManager(object):
    """Plan Rows and Columns on the Screen"""
    def __init__(self,screen_width = 1024,screen_height =768,card_width=825,
        card_height=1125,card_scale=0.10,mat_to_card_ratio=1.10,n_columns=7,n_rows=5):
        self.CardWidth = card_width  
        self.CardHeight = card_height
        self.ScreenWidth = screen_width
        self.ScreenHeight = screen_height
        self.CardScale = card_scale

        self.MatWidth, self.MatHeight = self.getMatSize(self.CardWidth,self.CardHeight,\
          self.CardScale,mat_to_card_ratio)

        self.VerticalOffset = self.MatHeight/2
        self.Column = self.getColumnSpacing(n_columns)
        self.Row = self.getRowSpacing(n_rows)

    def getMatSize(self,card_width=825,card_height = 1125, card_scale=0.15,mat_to_card_size_ratio=1.25):
        """Get the width of a card mat"""
         #do some math to get to the size of a mat
        scaled_card_width = card_width * card_scale
        mat_width = scaled_card_width * mat_to_card_size_ratio
        
        scaled_card_height = card_height * card_scale
        mat_height = scaled_card_height * mat_to_card_size_ratio
        return int(mat_width),int(mat_height)

    def getRowSpacing(self,n_rows, vertical_mat_margin = 0.10):
        row_y_coords = []
        first_y = self.MatHeight/2 + self.MatHeight * vertical_mat_margin + self.VerticalOffset
        y_spacing = self.MatHeight + self.MatHeight * vertical_mat_margin
        for i in range(n_rows):
            curr_y_coord = int(first_y + i * y_spacing)
            row_y_coords.append(curr_y_coord)
        return row_y_coords

    def getColumnSpacing(self,n_columns=7,horizontal_mat_margin=0.10):
        """Return a list of column X coordinates"""
         
        column_x_coords = []
        first_x = self.MatWidth/2 + self.MatWidth * horizontal_mat_margin
        x_spacing = self.MatWidth + self.MatWidth * horizontal_mat_margin
        for i in range(n_columns):
            curr_x_coord = int(first_x + i * x_spacing) 
            column_x_coords.append(curr_x_coord)         
        return column_x_coords
   

class DraftView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

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

        self.VerticalCardStackOffset = int(1/8 * self.CardHeight)
        
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


        #Save the y position of the top row of cards (7 piles)
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
        deck_color = arcade.csscolor.DARK_SLATE_BLUE
        discard_color = arcade.csscolor.DARK_ORANGE

         
        # Create the seven middle piles
        n_middle_piles = 7
        for i in range(n_middle_piles):
            pile = arcade.SpriteSolidColor(self.MatWidth, self.MatHeight,\
              mat_color)
            pile.position = self.CardStartX +\
              i * self.XSpacing,self.TopRowY
            
            self.MatList.append(pile)        
        
        #Deal a cards equally among middle piles
        current_mat = 0
        for i,card in enumerate(self.CardList):
            if current_mat >= len(self.MatList):
                current_mat = 0
            self.CardList[i].position = self.MatList[current_mat].position
            current_mat +=1 


        #Create objects to hold our actual deck and discarded pile
        self.Deck = []
        self.Discard = []
        

        #Ensure we aren't holding any cards at first
        self.HeldCards = []
        self.HeldCardsOriginalPosition = []


        self.DeckSize = 15
        self.DiscardSize = 10

        # Create the mat for the drafted Deck cards
        self.DeckMat = arcade.SpriteSolidColor(self.MatWidth,\
          self.MatHeight*2,deck_color)
       
        # Set the Deck position 
        self.DeckMat.position =\
          self.CardStartX, self.CardStartY + self.MatHeight/2
        
        self.MatList.append(self.DeckMat)

        #Put some text right below the deck mat
        title_font_size = 20
        self.DeckReport = arcade.Text(
            f"Deck:{len(self.Deck)} / {self.DeckSize}",
            self.CardStartX - self.MatWidth/2,
            self.MiddleRowY + self.MatHeight/4,
            deck_color,
            title_font_size,
            bold = True,
            width=self.ScreenWidth/2,
            align="left",
        )

        #Create a mat for discarded cards        
        self.DiscardMat = arcade.SpriteSolidColor(self.MatWidth,\
          self.MatHeight*2,discard_color)

        self.DiscardMat.position =\
          self.CardStartX + self.XSpacing*2, self.CardStartY + self.MatHeight/2

        self.MatList.append(self.DiscardMat)
 
        self.DiscardReport = arcade.Text(
            f"Discard:{len(self.Discard)} / {self.DiscardSize}",
            self.CardStartX + self.XSpacing - self.MatWidth/2,
            self.MiddleRowY + self.MatHeight/4,
            discard_color,
            title_font_size,
            bold = True,
            width=self.ScreenWidth/2,
            align="center",
        )
    
        self.Title = arcade.Text(
            "Drag Cards to your Deck (blue)\n or to Discard (red)",
            self.CardStartX+self.XSpacing*3-self.MatWidth/2,
            self.CardStartY,   
            arcade.color.BLACK,
            title_font_size,
            bold = True,
            width=self.ScreenWidth/2,
            align="center",
        )

    
    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top)        """
        if card.Active:
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
        self.DeckReport.draw()
        self.DiscardReport.draw()

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
            #Check if cards should be added to deck or discard
            if mat is self.DeckMat and len(self.Deck) < self.DeckSize and primary_card.Active:
                # Success, don't reset position of cards
                reset_position = False
                primary_card.Active = False
                #print("Current cards:",[c.name+"\n" for c in self.Deck])
                self.DeckReport.text = f"Deck:{len(self.Deck)} / {self.DeckSize}"
                
                # For each held card, move it to the pile we dropped on
                for i, dropped_card in enumerate(self.HeldCards):
                    # Move cards to proper position
                    self.Deck.append(dropped_card)
                    dropped_card.Active = False
                    vertical_card_offset = self.get_card_pile_offset(self.Deck,self.DeckSize)
                    dropped_card.position = mat.center_x, mat.center_y + vertical_card_offset

    
                if len(self.Deck) == self.DeckSize:
                    self.writeDeckToFile(self.DeckFile)
                    self.writeDeckToFile("../data/decks/latest_player_draft.tsv")
                    
                    #Draft Finished! Exit to Game!
                    game_view = GameView()
                    game_view.setup(draft=self)
                    self.window.show_view(game_view)  
            elif mat is self.DiscardMat and len(self.Discard) < self.DiscardSize and primary_card.Active:
                # Success, don't reset position of cards
                primary_card.Active = False
                reset_position = False
                
                # For each held card, move it to the pile we dropped on
                for i, dropped_card in enumerate(self.HeldCards):
                    # Move cards to proper position
                    self.Discard.append(dropped_card)
                    dropped_card.Active = False
                    vertical_card_offset = self.get_card_pile_offset(self.Discard,self.DiscardSize)
                    dropped_card.position = mat.center_x, mat.center_y + vertical_card_offset

                self.DiscardReport.text = f"Discard:{len(self.Discard)} / {self.DiscardSize}"
        
        if reset_position:
            # Where-ever we were dropped, it wasn't valid. 
            # Reset the each card's position to its original spot.
            for i, returned_card in enumerate(self.HeldCards):
                returned_card.position = self.HeldCardsOriginalPosition[i]
                
        for c in self.HeldCards:
            c.scale = self.CardScale

        self.HeldCards = []
        self.HeldCardsOriginalPosition = []
    
    def get_card_pile_offset(self,card_stack,max_stack_size):
        """Get an offset for each card in pile"""
        return -1 * len(card_stack)*self.VerticalCardStackOffset + int(round(max_stack_size/2))*self.VerticalCardStackOffset

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
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    instruction_view = InstructionView()
    window.show_view(instruction_view)
    instruction_view.setup()
    arcade.run()

if __name__ == "__main__":
    main()
