import numpy as np
import matplotlib.pyplot as plt

# Increase resolution to 1000x1000 for crisp, high-detail coastlines
SIZE = 1000
np.random.seed(99)

# Create high-resolution coordinate grid
x = np.linspace(-1, 1, SIZE)
y = np.linspace(-1, 1, SIZE)
X, Y = np.meshgrid(x, y)

# 1. POLAR PROJECTION TRANSFORM CONSTRAINTS
R = np.sqrt(X ** 2 + Y ** 2)
Theta = np.arctan2(Y, X)

# Normalizing coordinates relative to the Earth core disc boundary (R <= 0.40)
lat = 1.0 - (R / 0.40)
lon = (Theta + np.pi) / (2 * np.pi)  # 0.0 to 1.0 sweeping clockwise smoothly


# --------------------------------------------------------
# 2. SEEDING CRISP, HIGH-RESOLUTION GEOMETRIC TEMPLATES
# --------------------------------------------------------
def get_high_res_polar_template(lat, lon, X, Y):
    """
    Constructs highly-detailed mathematical profiles for Earth continents
    warped correctly into the polar aspect configuration.
    """
    land = np.zeros(lat.shape, dtype=bool)

    # --- ARCTIC / GREENLAND CORE ---
    arctic_cap = lat > 0.90
    greenland = (lon > 0.39) & (lon < 0.44) & (lat > 0.68) & (lat <= 0.88)

    # --- NORTH AMERICA (Detailed Silhouette) ---
    na_base = (lon > 0.16) & (lon < 0.39) & (lat > 0.35) & (lat <= 0.90)
    # Carving out the Hudson Bay cavity procedurally by removing a specific patch
    hudson_bay = (lon > 0.28) & (lon < 0.34) & (lat > 0.52) & (lat < 0.68)
    north_america = na_base & ~hudson_bay

    # --- SOUTH AMERICA (Stretched Patagonia Wedge) ---
    sa_zone = (lon > 0.25) & (lon < 0.37) & (lat > 0.02) & (lat <= 0.35)
    # Mathematical taper: narrows progressively as it approaches the outer rim (lat -> 0)
    sa_width_restriction = (lon - 0.25) > (0.35 - lat) * 0.22
    south_america = sa_zone & sa_width_restriction

    # --- EURASIA (Massive Crescent Ring) ---
    eurasia_main = (lon > 0.44) & (lon < 0.96) & (lat > 0.36) & (lat <= 0.90)
    # Adding defined structural variations for Europe vs East Asia
    mediterranean_cut = (lon > 0.45) & (lon < 0.52) & (lat > 0.36) & (lat < 0.44)
    eurasia = eurasia_main & ~mediterranean_cut

    # --- AFRICA (Broad Top, Tapered Bottom) ---
    africa_zone = (lon > 0.46) & (lon < 0.64) & (lat > 0.04) & (lat <= 0.44)
    # Taper Africa toward South Africa at the outer edge
    africa_taper = (lon - 0.46) > (0.44 - lat) * 0.18
    africa = africa_zone & africa_taper

    # --- AUSTRALIA (Isolated Southeastern Pod) ---
    australia = (lon > 0.76) & (lon < 0.91) & (lat > 0.06) & (lat <= 0.26)

    # Combine all specific high-resolution continent layers
    land = arctic_cap | greenland | north_america | south_america | eurasia | africa | australia
    return land


# Compile the base polar layout template
earth_base_mask = get_high_res_polar_template(lat, lon, X, Y)
earth_base_mask = earth_base_mask & (R <= 0.40)  # Absolute clip at Earth border


# --------------------------------------------------------
# 3. HIGH-RESOLUTION MICRO-NOISE FRACTIONING
# --------------------------------------------------------
def detailed_fractal_noise(X, Y, octaves=7, persistence=0.52, lacunarity=2.2):
    """Adds sharp micro-details to simulate islands and realistic coastlines."""
    noise = np.zeros(X.shape)
    amplitude = 1.0
    frequency = 6.0  # Increased starting frequency to prevent bulky blobs
    for i in range(octaves):
        shift = i * 53.1
        layer = np.sin(frequency * X + shift) * np.cos(frequency * Y + shift)
        layer += np.cos(frequency * 0.85 * Y - shift) * np.sin(frequency * 1.15 * X + shift)
        noise += (1.0 - np.abs(layer)) * amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return (noise - noise.min()) / (noise.max() - noise.min())


noise_map = detailed_fractal_noise(X, Y)
biome_noise_1 = detailed_fractal_noise(X + 15, Y - 15, octaves=4)
biome_noise_2 = detailed_fractal_noise(X - 30, Y + 30, octaves=4)

# Apply a delicate, tight warp factor so it preserves the template geometry
distorted_R = R + (noise_map * 0.02 - 0.01)

# Blending the map template with fractal details
# Higher template weighting (0.65) ensures the layout mimics your image accurately
high_res_terrain = (earth_base_mask.astype(float) * 0.65) + (noise_map * 0.35)

# --------------------------------------------------------
# 4. FIVE-TIER RADIUS MAP COMPOSITION
# --------------------------------------------------------
R_EARTH_WORLD = 0.40
R_ICE_WALL_1 = 0.45
R_OUTER_ZONE_1 = 0.64
R_ICE_WALL_2 = 0.68
R_OUTER_ZONE_2 = 0.88
R_MAX_EDGE = 1.00

color_map = np.zeros((SIZE, SIZE, 3))

for i in range(SIZE):
    for j in range(SIZE):
        radius = distorted_R[i, j]
        raw_r = R[i, j]

        if raw_r > R_MAX_EDGE:
            color_map[i, j] = [0.01, 0.01, 0.03]  # The outer void

        elif radius > R_OUTER_ZONE_2 and raw_r <= R_MAX_EDGE:
            color_map[i, j] = [0.84, 0.91, 0.98]  # Final Perimeter Ice Wall

        elif radius > R_ICE_WALL_2 and radius <= R_OUTER_ZONE_2:
            n2 = biome_noise_2[i, j]
            if n2 < 0.45:
                color_map[i, j] = [0.05, 0.07, 0.20]  # Outer Deep Twilight Sea
            elif n2 < 0.68:
                color_map[i, j] = [0.46, 0.12, 0.24]  # Crimson Forest
            else:
                color_map[i, j] = [0.24, 0.08, 0.38]  # Obsidian spires

        elif radius > R_OUTER_ZONE_1 and radius <= R_ICE_WALL_2:
            color_map[i, j] = [0.74, 0.86, 0.94]  # Middle Ice Wall Ring

        elif radius > R_ICE_WALL_1 and radius <= R_OUTER_ZONE_1:
            n1 = biome_noise_1[i, j]
            if n1 < 0.46:
                color_map[i, j] = [0.04, 0.15, 0.34]  # Intermediate Sea
            elif n1 < 0.70:
                color_map[i, j] = [0.10, 0.38, 0.20]  # Taiga / Pine Biome
            else:
                color_map[i, j] = [0.64, 0.52, 0.30]  # Golden Steppes

        elif radius > R_EARTH_WORLD and radius <= R_ICE_WALL_1:
            color_map[i, j] = [0.88, 0.94, 0.98]  # First Inner Ice Wall (Antarctic Rim)

        elif radius <= R_EARTH_WORLD:
            val = high_res_terrain[i, j]

            # Explicitly paint the central white polar circle if it overlaps land height
            if lat[i, j] > 0.90 and val > 0.42:
                color_map[i, j] = [0.96, 0.98, 1.00]
            elif val < 0.54:
                color_map[i, j] = [0.08, 0.26, 0.55]  # Ocean
            elif val < 0.56:
                color_map[i, j] = [0.84, 0.80, 0.64]  # Coastlines / Sand Bars
            elif val < 0.72:
                color_map[i, j] = [0.20, 0.54, 0.26]  # Continental Landmass (Green fields)
            else:
                color_map[i, j] = [0.44, 0.40, 0.36]  # Mountainous Ridges

# Output the optimized render
plt.figure(figsize=(12, 12))
plt.imshow(color_map)
plt.title("High-Resolution Procedural Polar Earth & Outer Ring Systems", fontsize=11, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()
