# v0_1/world/generator.py

import random
from noise import pnoise2

from v0_1.config.settings import WORLD_SEED, CHUNK_SIZE
from v0_1.world.biome import get_biome

OCTAVES = 6


def _noise(x, y, scale, seed_offset=0):
    n = pnoise2(
        x / scale,
        y / scale,
        octaves=OCTAVES,
        repeatx=999999,
        repeaty=999999,
        base=WORLD_SEED + seed_offset
    )

    # sharpen terrain contrast
    n = n * 1.2 - 0.1

    return max(0.0, min(1.0, (n + 1) / 2))


def warp(wx, wy):
    """
    Domain warping: distorts input coordinates
    to create more natural terrain shapes.
    """

    ox = (pnoise2(wx / 80.0, wy / 80.0, base=WORLD_SEED + 999) +
        0.5 * pnoise2(wx / 40.0, wy / 40.0, base=WORLD_SEED + 888)
         ) / 1.5 * 12

    oy = (pnoise2(wx / 80.0, wy / 80.0, base=WORLD_SEED + 999) +
          0.5 * pnoise2(wx / 40.0, wy / 40.0, base=WORLD_SEED + 888)
          ) / 1.5 * 12

    return wx + ox, wy + oy

def generate_tile(wx, wy):
    # 🌍 DOMAIN WARP (KEY UPGRADE)
    wx, wy = warp(wx, wy)

    elevation = _noise(wx, wy, 120.0, 1)
    moisture = _noise(wx, wy, 200.0, 2)
    temperature = _noise(wx, wy, 250.0, 3)

    biome = get_biome(elevation, moisture, temperature)

    tile = {
        "elevation": elevation,
        "moisture": moisture,
        "temperature": temperature,
        "biome": biome,
        "objects": []
    }

    # Add simple resources
    if biome == "FOREST" and random.random() < 0.2:
        tile["objects"].append("TREE")

    if biome == "MOUNTAIN" and random.random() < 0.2:
        tile["objects"].append("STONE")

    return tile


def generate_chunk(cx, cy):

    chunk = {
        "chunk_x": cx,
        "chunk_y": cy,
        "tiles": [],
        "pois": []
    }

    for y in range(CHUNK_SIZE):
        row = []

        for x in range(CHUNK_SIZE):

            wx = cx * CHUNK_SIZE + x
            wy = cy * CHUNK_SIZE + y

            row.append(generate_tile(wx, wy))

        chunk["tiles"].append(row)

    # Add POIs (simple early version)
    if random.random() < 0.2:
        chunk["pois"].append({
            "type": "MINE_ENTRANCE",
            "x": random.randint(0, CHUNK_SIZE-1),
            "y": random.randint(0, CHUNK_SIZE-1)
        })

    return chunk