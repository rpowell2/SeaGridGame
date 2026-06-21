import cv2
import numpy as np
import matplotlib.pyplot as plt


# --- 1. MOUNTAIN HEIGHT NOISE ENGINE ---
def get_noise_2d(X, Y, scale=1.0):
    def hash2d(x, y):
        x_sin = np.sin(x * 12.9898 + y * 78.233) * 43758.5453123
        return x_sin - np.floor(x_sin)

    def smooth_noise(x, y):
        xf, yf = x - np.floor(x), y - np.floor(y)
        xi, yi = np.floor(x).astype(int), np.floor(y).astype(int)

        u = xf * xf * (3.0 - 2.0 * xf)
        v = yf * yf * (3.0 - 2.0 * yf)

        n00 = hash2d(xi, yi)
        n10 = hash2d(xi + 1, yi)
        n01 = hash2d(xi, yi + 1)
        n11 = hash2d(xi + 1, yi + 1)

        return n00 * (1.0 - u) * (1.0 - v) + n10 * u * (1.0 - v) + n01 * (1.0 - u) * v + n11 * u * v

    nx, ny = X * scale * 0.007, Y * scale * 0.007
    return ((smooth_noise(nx, ny) * 0.5 + smooth_noise(nx * 2.02, ny * 2.02) * 0.25 + smooth_noise(nx * 4.05,
                                                                                                   ny * 4.05) * 0.125) - 0.4) * 2.0


# --- 2. DIRECT TEMPLATE LOOKUP GENERATOR ---
def generate_precise_chunk(min_x, max_x, min_y, max_y, resolution, template_path="map.jpg"):
    img = cv2.imread(template_path)
    if img is None:
        raise FileNotFoundError(f"Could not load '{template_path}'. Ensure the image is in this directory.")

    img_h, img_w, _ = img.shape
    img_cx, img_cy = img_w // 2, img_h // 2
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    y_coords = np.linspace(min_y, max_y, resolution)
    x_coords = np.linspace(min_x, max_x, resolution)
    X, Y = np.meshgrid(x_coords, y_coords)
    dist_from_center = np.sqrt(X ** 2 + Y ** 2)

    inner_radius = 4000.0
    ice_wall_start = 3620.0

    pixel_radius = min(img_cx, img_cy) * 0.93
    unit_to_pixel_factor = pixel_radius / ice_wall_start

    pixel_x = img_cx + (X * unit_to_pixel_factor)
    pixel_y = img_cy - (Y * unit_to_pixel_factor)

    px_clipped = np.clip(pixel_x, 0, img_w - 1).astype(int)
    py_clipped = np.clip(pixel_y, 0, img_h - 1).astype(int)

    corrected_py = img_h - 1 - py_clipped

    sampled_hsv = img_hsv[corrected_py, px_clipped]
    H = sampled_hsv[:, :, 0]
    S = sampled_hsv[:, :, 1]
    V = sampled_hsv[:, :, 2]

    is_red_ring = (H >= 0) & (H <= 12) & (S > 40)
    is_blue_ocean = (H >= 85) & (H <= 135) & (S > 25)

    # Generate the initial raw land mask layout
    raw_land = (dist_from_center < ice_wall_start) & (~is_blue_ocean) & (~is_red_ring)

    # --- AUTOMATED STRUCTURAL LINE HEALER ---
    # Convert our boolean land layer into a standard OpenCV 8-bit binary mask format
    land_mask_uint8 = (raw_land * 255).astype(np.uint8)

    # Step A: Close gaps to heal the thin dashed equator cuts inside South America and Africa
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    land_mask_uint8 = cv2.morphologyEx(land_mask_uint8, cv2.MORPH_CLOSE, kernel_close)

    # Step B: Open shapes to dissolve the thin floating land segments out in the open ocean channels
    kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    land_mask_uint8 = cv2.morphologyEx(land_mask_uint8, cv2.MORPH_OPEN, kernel_open)

    # Convert back into a reliable boolean mask for NumPy processing
    land_mask = land_mask_uint8 == 255

    biome_map = np.ones_like(X, dtype=int)

    is_desert_pixel = (H >= 8) & (H <= 32) & (S > 25) & (V > 100) & land_mask
    biome_map[is_desert_pixel] = 2

    is_ice_pixel = (V > 200) & (S < 45) & land_mask
    biome_map[is_ice_pixel] = 3

    # --- PROCEDURAL MAP LAYER ADDITIONS ---
    base_noise = get_noise_2d(X, Y, scale=1.0)

    is_south_america = (X < -500) & (Y < 500) & land_mask

    is_andes_coast = is_south_america & (X < -2300)
    mountain_spine = (X * -0.0004) + (np.sin(Y * 0.008) * 0.15)
    biome_map[is_andes_coast & (mountain_spine > 1.05) & (biome_map != 3)] = 5

    elevation_noise = get_noise_2d(X, Y, scale=3.5)
    biome_map[land_mask & (~is_south_america) & (elevation_noise > 0.50) & (biome_map == 1)] = 5

    # Generate Coastline Borders
    is_edge = land_mask & (
            (~np.roll(land_mask, 1, axis=0)) | (~np.roll(land_mask, -1, axis=0)) |
            (~np.roll(land_mask, 1, axis=1)) | (~np.roll(land_mask, -1, axis=1))
    )
    is_edge &= (dist_from_center < (ice_wall_start - 30.0))
    biome_map[is_edge] = 6

    # Global structural override: Ice Wall Ring Frame
    ice_ring_mask = (dist_from_center >= ice_wall_start) & (dist_from_center <= inner_radius)
    land_mask[ice_ring_mask] = True
    biome_map[ice_ring_mask] = 3

    # Infinite Outer Procedural Space Generation
    outer_space_mask = dist_from_center > inner_radius
    if np.any(outer_space_mask):
        distance_past_wall = dist_from_center[outer_space_mask] - inner_radius
        is_past_ocean_moat = distance_past_wall > 400.0
        zone_0_mask = ((distance_past_wall - 400.0) // 3000.0).astype(int) == 0

        outer_land_noise_flat = get_noise_2d(X, Y, scale=1.5)[outer_space_mask]
        z0_land = (outer_land_noise_flat > 0.18)

        land_mask[outer_space_mask] = np.where(zone_0_mask & is_past_ocean_moat, z0_land, land_mask[outer_space_mask])
        biome_map[outer_space_mask] = np.where(zone_0_mask & is_past_ocean_moat & z0_land, 3,
                                               biome_map[outer_space_mask])

    # --- 3. GRAPHICS SHADING IMAGES SETUP ---
    chunk_img = np.zeros((resolution, resolution, 3))

    ocean_blend = np.clip((base_noise + 0.4) / 0.8, 0, 1)
    for c in range(3):
        deep_color = [0.10, 0.32, 0.52][c]
        shallow_color = [0.16, 0.44, 0.64][c]
        chunk_img[~land_mask, c] = deep_color + ocean_blend[~land_mask] * (shallow_color - deep_color)

    # Terrestrial color mappings
    chunk_img[land_mask & (biome_map == 1)] = [0.38, 0.58, 0.28]  # Plains Green
    chunk_img[land_mask & (biome_map == 2)] = [0.84, 0.75, 0.52]  # Desert Sand Tan
    chunk_img[land_mask & (biome_map == 3)] = [0.96, 0.96, 0.98]  # Greenland & Ice Wall White
    chunk_img[land_mask & (biome_map == 5)] = [0.46, 0.46, 0.48]  # Mountain Spine Gray
    chunk_img[land_mask & (biome_map == 6)] = [0.12, 0.08, 0.05]  # Dark Outline Coast Borders

    return chunk_img


if __name__ == "__main__":
    world_chunk = generate_precise_chunk(-6000, 6000, -6000, 6000, 850, template_path="map.jpg")

    plt.figure(figsize=(9, 9))
    plt.imshow(world_chunk, extent=[-6000, 6000, -6000, 6000])
    plt.title("Direct Raster-Procedural Balanced Projection Map", fontsize=12)
    plt.axis('off')
    plt.show()
