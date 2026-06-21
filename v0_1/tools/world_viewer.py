# v0_1/tools/world_viewer.py

import os
from PIL import Image

from v0_1.world.storage import load_chunk
from v0_1.config.settings import CHUNK_SIZE
from v0_1.config.settings import WORLD_RADIUS


# ------------------------------------------------------------
# BIOME COLOR MAP
# ------------------------------------------------------------

BIOME_COLORS = {
    "OCEAN": (0, 70, 180),
    "BEACH": (238, 214, 175),
    "PLAINS": (80, 200, 80),
    "FOREST": (20, 120, 20),
    "SWAMP": (40, 90, 40),
    "DESERT": (210, 190, 120),
    "TUNDRA": (170, 170, 170),
    "SNOW": (245, 245, 245),
    "MOUNTAIN": (110, 110, 110),
}


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

OUTPUT_FILE = "world.png"

CHUNK_RADIUS = WORLD_RADIUS   # must match generator range, Example: (-2..2)

PIXEL_SCALE = 1    # 1 tile = 1 pixel (fast + simple)


# ------------------------------------------------------------
# LOAD CHUNK
# ------------------------------------------------------------

def get_chunk(cx, cy):
    chunk = load_chunk(cx, cy)
    return chunk


# ------------------------------------------------------------
# MAIN RENDER
# ------------------------------------------------------------

def render_world():

    chunks = {}

    min_x = -CHUNK_RADIUS
    max_x = CHUNK_RADIUS
    min_y = -CHUNK_RADIUS
    max_y = CHUNK_RADIUS

    world_width = (max_x - min_x + 1) * CHUNK_SIZE
    world_height = (max_y - min_y + 1) * CHUNK_SIZE

    img = Image.new("RGB", (world_width, world_height))

    print("Rendering world...")

    for cy in range(min_y, max_y + 1):
        for cx in range(min_x, max_x + 1):

            chunk = get_chunk(cx, cy)

            if not chunk:
                continue

            base_x = (cx - min_x) * CHUNK_SIZE
            base_y = (cy - min_y) * CHUNK_SIZE

            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):

                    tile = chunk["tiles"][y][x]
                    biome = tile["biome"]

                    color = BIOME_COLORS.get(
                        biome,
                        (255, 0, 255)  # debug magenta
                    )

                    px = base_x + x
                    py = base_y + y

                    img.putpixel((px, py), color)

    img.save(OUTPUT_FILE)

    print(f"Saved {OUTPUT_FILE}")


# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if __name__ == "__main__":
    render_world()