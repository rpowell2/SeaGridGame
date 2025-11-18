import math
import random
import arcade

# Set up the constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "SeaGridGame Test"
IMAGE_ROTATION = -90

class Resource(arcade.Sprite):
    def __init__(self):
        super().__init__("C:\\Dev\\SeaGridGame\\kenney_pirate-pack\\PNG\\Default size\\Tiles\\tile_71.png")

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("C:\\Dev\\SeaGridGame\\kenney_pirate-pack\\PNG\\Default size\\Ships\\dinghySmall1.png")

        self._destination_point = None
        self.speed = 300
        self.rot_speed = 0.1

    @property
    def destination_point(self):
        return self._destination_point
    
    @destination_point.setter
    def destination_point(self, destination_point):
        self._destination_point = destination_point
        self.change_x = 0.0
        self.change_y = 0.0
    
    def update(self, delta_time: float = 1/60):
        if not self._destination_point:
            self.change_x = 0
            self.change_y = 0
            return
        
        start_x = self.center_x
        start_y = self.center_y

        dest_x = self._destination_point[0]
        dest_y = self._destination_point[1]

        target_angle = arcade.math.get_angle_degrees(start_x, start_y, dest_x, dest_y)
        current_angle = self.angle - IMAGE_ROTATION
        
        new_angle = arcade.math.lerp_angle(current_angle, target_angle, self.rot_speed)

        self.angle = new_angle + IMAGE_ROTATION
        angle_diff = abs(target_angle - new_angle)
        if angle_diff < 0.1 or 359.9 < angle_diff:
            self.angle = target_angle + IMAGE_ROTATION
            target_radians = math.radians(target_angle)
            self.change_x = math.cos(-target_radians) * self.speed
            self.change_y = math.sin(-target_radians) * self.speed
        
        traveling = False
        if(abs(self.center_x - dest_x) < abs(self.change_x * delta_time)):
            self.center_x = dest_x
        else:
            self.center_x += self.change_x * delta_time
            traveling = True
        
        if(abs(self.center_y - dest_y) < abs(self.change_y * delta_time)):
            self.center_y = dest_y
        else:
            self.center_y += self.change_y * delta_time
            traveling = True
        
        if not traveling:
            self._destination_point = None

class GameView(arcade.View):
    """
    Main Game Window
    """

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DEEP_SKY_BLUE        
        self.player_sprite = None
        self.player_list = None
        self.resource_list = None

        self.background_color = arcade.csscolor.DEEP_SKY_BLUE
    
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.resource_list = arcade.SpriteList()
        self.player_sprite = Player()
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        resource_amount = random.randint(1,10)
        for i in range(resource_amount):
            resource_sprite = Resource()
            resource_sprite.center_x = random.randint(0,WINDOW_HEIGHT)
            resource_sprite.center_y = random.randint(0,WINDOW_WIDTH)
            self.resource_list.append(resource_sprite)
        
        pass

    def on_draw(self):
        self.clear()
        self.player_list.draw()
        self.resource_list.draw()
    
    def on_update(self, delta_time):
        self.player_list.update(delta_time)
    
    def on_mouse_press(self, x, y, button, key_modifiers):
        if(button == arcade.MOUSE_BUTTON_LEFT):
            self.player_sprite.destination_point = x, y

def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()