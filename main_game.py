import arcade

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "SeaGridGame Test"

def main():
    """ Main method """
    arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.set_background_color(arcade.color.AMAZON)
    arcade.run()

if __name__ == "__main__":
    main()