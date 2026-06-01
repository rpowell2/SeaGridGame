# v0_1/tools/world_generator.py

from v0_1.world.generator import generate_chunk
from v0_1.world.storage import save_chunk

def main():

    print("Generating spawn chunks...")

    for x in range(-2, 3):
        for y in range(-2, 3):

            chunk = generate_chunk(x, y)
            save_chunk(chunk)

            print(f"Generated chunk {x},{y}")

if __name__ == "__main__":
    main()