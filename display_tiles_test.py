from PIL import Image, ImageDraw
import os
from utils import ark_window
from elements import get_element
from scenarios import Store

"""
Set KEYS_TO_DISPLAY to a list of keys from Store._tile_info to render only those.
Leave empty to render all keys.
Examples: ["top_left", "center"], ["circle_position_left", "circle_position_right"]
"""
KEYS_TO_DISPLAY = ['available_position'] #['circle_position_left', 'circle_position_right', 'circle_position_upper', 'circle_position_lower']  # type: ignore[var-annotated]


def draw_store_tiles_outline(img: Image.Image):
    draw = ImageDraw.Draw(img)
    # Rectangles will be drawn with a 1px red outline
    outline = (255, 0, 0)
    width = 1
    # Each tile is 355x355 as per elements.py comments
    tile_w = 355
    tile_h = 355

    for i in range(1, 11):
        el = get_element(f"store_tile_{i}")
        if not el or not el.click_coords:
            continue
        x, y = el.click_coords
        # Draw rectangle: top-left (x, y) to bottom-right (x+tile_w-1, y+tile_h-1)
        draw.rectangle([x, y, x + tile_w - 1, y + tile_h - 1], outline=outline, width=width)


def draw_tile_info_points(img: Image.Image, keys_to_display=None):
    draw = ImageDraw.Draw(img)
    fill = (255, 0, 0)
    store = Store()
    for i in range(1, 11):
        try:
            info = store._tile_info(i)
        except Exception:
            continue
        for key, data in info.items():
            if keys_to_display and key not in keys_to_display:
                continue
            coords = data.get("coords") if isinstance(data, dict) else None
            if not coords:
                continue
            x, y = coords
            # 2x2 red square (inclusive box: x..x+1, y..y+1)
            draw.rectangle([x, y, x + 1, y + 1], fill=fill)


def main():
    # Capture current window frame (already cropped to game window)
    frame = ark_window.get_frame(fresh=True)
    img = Image.fromarray(frame)

    draw_store_tiles_outline(img)
    draw_tile_info_points(img, keys_to_display=KEYS_TO_DISPLAY or None)

    # Save to logs directory
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    out_path = os.path.join(logs_dir, "store_tiles_overlay.png")
    img.save(out_path)
    print(f"Saved overlay to {out_path}")


if __name__ == "__main__":
    main()


