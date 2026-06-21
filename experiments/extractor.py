import cv2
import numpy as np
import json


def extract_world_polygons(image_path, output_json_path, scale_factor=4.0):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not open '{image_path}'. Make sure it is named correctly and in this folder.")

    h, w, _ = img.shape
    center_x, center_y = w // 2, h // 2

    # 1. Convert to HSV to separate color type (Hue) from intensity (Saturation)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)

    # 2. Isolate the Blue Ocean (Hue 85-135)
    is_blue_ocean = (hue >= 85) & (hue <= 135) & (saturation > 30)

    # Land is anything inside the main circular disc that is NOT the blue ocean
    Y, X = np.ogrid[:h, :w]
    dist_from_img_center = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
    max_inner_disk_radius = min(center_x, center_y) * 0.94
    inside_world_disc = dist_from_img_center < max_inner_disk_radius

    land_mask = np.zeros_like(saturation, dtype=np.uint8)
    land_mask[inside_world_disc & ~is_blue_ocean] = 255

    # Filter out lone grid lines or text markers by removing small artifacts
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    land_mask = cv2.morphologyEx(land_mask, cv2.MORPH_OPEN, kernel)

    # 3. Extract Sub-Terrains based on true colors
    # Deserts = Yellow/Tan hues
    desert_mask = (hue >= 10) & (hue <= 32) & (saturation > 25) & (land_mask == 255)
    # White Ice Caps = Highly reflective white pixels with little to no color saturation
    ice_mask = (value > 210) & (saturation < 40) & inside_world_disc & (land_mask == 255)

    # Clean function to turn OpenCV tracks into 100% stable Cartesian paths
    def clean_contour_to_list(contour):
        epsilon = 0.0006 * cv2.arcLength(contour, True)  # Low value preserves maximum geometric detail
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Squeeze out extra array dimensions to safely prevent unpacking bugs
        pts = approx.squeeze()
        if pts.ndim != 2:
            return []

        coords = []
        for p in pts:
            px, py = float(p[0]), float(p[1])
            # Center coordinates around (0,0) and flip Y to line up with standard 2D cartesian grids
            cart_x = (px - center_x) * scale_factor
            cart_y = (center_y - py) * scale_factor
            coords.append([round(cart_x, 1), round(cart_y, 1)])
        return coords

    blueprint = {
        "world_settings": {
            "inner_rim_radius": float(max_inner_disk_radius * scale_factor),
            "ice_wall_thickness": float(max_inner_disk_radius * scale_factor * 0.06)
        },
        "continents": [],
        "deserts": [],
        "ice_caps": []
    }

    # Find and convert Landmass Shapes
    contours, _ = cv2.findContours(land_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i, c in enumerate(contours):
        if cv2.contourArea(c) > 15:
            poly = clean_contour_to_list(c)
            if poly: blueprint["continents"].append({"id": i + 1, "polygon": poly})

    # Find and convert Desert Shapes
    d_contours, _ = cv2.findContours(desert_mask.astype(np.uint8) * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in d_contours:
        if cv2.contourArea(c) > 10:
            poly = clean_contour_to_list(c)
            if poly: blueprint["deserts"].append(poly)

    # Find and convert Ice Sheet Shapes
    i_contours, _ = cv2.findContours(ice_mask.astype(np.uint8) * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in i_contours:
        if cv2.contourArea(c) > 10:
            poly = clean_contour_to_list(c)
            if poly: blueprint["ice_caps"].append(poly)

    with open(output_json_path, 'w') as f:
        json.dump(blueprint, f, indent=2)

    print(f"Success! Vector blueprint created with {len(blueprint['continents'])} detailed landmasses.")


if __name__ == "__main__":
    extract_world_polygons("map.jpg", "world_blueprint.json", scale_factor=4.0)
