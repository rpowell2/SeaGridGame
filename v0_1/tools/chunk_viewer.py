# v0_1/tools/chunk_viewer.py

from v0_1.world.storage import load_chunk

def inspect(cx, cy):

    chunk = load_chunk(cx, cy)

    if not chunk:
        print("No chunk found")
        return

    print(f"Chunk {cx},{cy}")
    print("POIs:", chunk["pois"])

    sample = chunk["tiles"][0][0]
    print("Sample tile:", sample)

if __name__ == "__main__":
    inspect(0, 0)