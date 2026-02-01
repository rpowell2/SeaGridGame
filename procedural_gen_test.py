import arcade
from random import randrange

# screen size constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Procedural Gen Test")
arcade.set_background_color(arcade.color.BLUE_YONDER)
arcade.start_render()

# draw ground
arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT/3, arcade.color.MSU_GREEN)

# draw sun
arcade.draw_circle_filled(50, SCREEN_HEIGHT-50, 75, arcade.color.SUNSET)
arcade.draw_circle_outline(50, SCREEN_HEIGHT-50, 75, arcade.color.BURNT_ORANGE)
# draw trees
def draw_tree(xpos, ypos):
    arcade.draw_rect_filled(arcade.rect.XYWH(xpos, ypos, 15, 80), arcade.color.WOOD_BROWN)
    arcade.draw_rect_outline(arcade.rect.XYWH(xpos, ypos, 15, 80), arcade.color.DARK_BROWN, 1)
    arcade.draw_circle_filled(xpos, ypos+25, 35, arcade.color.FERN_GREEN)
    arcade.draw_circle_outline(xpos, ypos+25, 35, arcade.color.ARMY_GREEN)


for i in range(25, SCREEN_WIDTH-25, 75):
    max_ypos = SCREEN_HEIGHT / 3
    draw_tree(randrange(i - 25, i + 25), randrange(int(max_ypos)))



# finish program, need to keep the window open
arcade.finish_render()
arcade.run()
