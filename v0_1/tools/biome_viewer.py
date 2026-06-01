# v0_1/tools/biome_viewer.py

from world.storage import load_chunk

def view(cx, cy):

    chunk = load_chunk(cx, cy)

    for row in chunk["tiles"]:
        print("".join(
            tile["biome"][0]
            for tile in row
        ))

if __name__ == "__main__":
    view(0, 0)