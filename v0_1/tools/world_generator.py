# v0_1/tools/world_generator.py

from v0_1.world.generator import generate_chunk
from v0_1.world.storage import save_chunk
from v0_1.config.settings import WORLD_RADIUS

def main():

    print("Generating spawn chunks...")

    world_sw_corner = -WORLD_RADIUS

    for x in range(world_sw_corner, WORLD_RADIUS + 1):
        for y in range(world_sw_corner, WORLD_RADIUS + 1):

            chunk = generate_chunk(x, y)
            save_chunk(chunk)

            print(f"Generated chunk {x},{y}")

if __name__ == "__main__":
    main()