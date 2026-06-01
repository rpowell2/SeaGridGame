# v0_1/world/biome.py

def get_biome(elevation, moisture, temperature):
    if 0.42 <= elevation < 0.46:
        return "BEACH"

    if elevation < 0.42:
        return "OCEAN"

    if elevation < 0.35:
        return "BEACH"

    if elevation > 0.80:
        return "MOUNTAIN"

    if temperature < 0.25:
        return "SNOW" if moisture > 0.5 else "TUNDRA"

    if moisture < 0.20:
        return "DESERT"

    if moisture > 0.70:
        return "SWAMP"

    if moisture > 0.50:
        return "FOREST"

    return "PLAINS"