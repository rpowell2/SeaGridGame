
# v0_1/world/storage.py

import os
import json

BASE_PATH = "data/world/chunks"


def chunk_path(cx, cy):
    return f"{BASE_PATH}/{cx}_{cy}.json"


def save_chunk(chunk):
    os.makedirs(BASE_PATH, exist_ok=True)

    with open(chunk_path(chunk["chunk_x"], chunk["chunk_y"]), "w") as f:
        json.dump(chunk, f)


def load_chunk(cx, cy):
    path = chunk_path(cx, cy)

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f)