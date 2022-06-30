"""
Run the Game.
"""
import arcade
import os

# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Draft Cards"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        #Relative scale of cards
        self.CardScale = 0.25
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
        
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self,card_dir="../data/images/cards/kingdom_of_kyberia"):
        """ Set up the game here. Call this function to restart the game. """
        # Sprite list with all the cards, no matter what pile they are in.
        self.CardList = arcade.SpriteList()
        card_list = [os.path.join(card_dir,f) for f in os.listdir(card_dir)]
        for i,card in enumerate(card_list):
            card_sprite = Card(card,scale=self.CardScale)
            card_sprite.position = (self.CardStartX,self.CardStartY)
            self.CardList.append(card_sprite)

        # List of cards we are dragging with the mouse
        self.HeldCards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.HeldCardsOriginalPosition = [] 

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        #Draw card list
        self.CardList.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        pass

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
        pass


class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, card_image_fp, scale=1):
        """ Card constructor """

        self.CardImage = card_image_fp


        # Call the parent
        super().__init__(self.CardImage, scale, hit_box_algorithm="None")






def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
