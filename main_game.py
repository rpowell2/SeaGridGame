import arcade

# Set up the constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "SeaGridGame Test"

class GameView(arcade.Window):
    """
    Main Game Window
    """

    def __init__(self):
        super().__init__(WINDOW_WIDTH,WINDOW_HEIGHT,WINDOW_TITLE)
        self.background_color = arcade.csscolor.SEA_GREEN
    
    def setup(self):
        pass

    def on_draw(self):
        self.clear()

def main():
    """ Main method """
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()