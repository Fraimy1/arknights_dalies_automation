from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from config import ELEMENT_COORDS


@dataclass
class UIElement:
    name: str
    # Optional pixel anchors: list of (x, y, expected_rgb)
    pixel_points: Optional[List[Tuple[int, int, Tuple[int, int, int]]]] = None
    # Optional small ROI for mean/median color sampling: (x, y, w, h)
    roi: Optional[Tuple[int, int, int, int]] = None
    # Optional template image path and threshold for matchTemplate
    template_path: Optional[str] = None
    template_threshold: float = 0.85
    # Optional preferred click coordinates
    click_coords: Optional[Tuple[int, int]] = None


def _as_rgb(rgb_or_none):
    if rgb_or_none is None:
        return None
    r, g, b = rgb_or_none
    return (int(r), int(g), int(b))


# Minimal registry seeded with known coordinates from current scenarios.
ELEMENTS: Dict[str, UIElement] = {
    "skip_button": UIElement(
        name="skip_button",
        pixel_points=[(ELEMENT_COORDS.get("skip_button", (0, 0))[0],
                      ELEMENT_COORDS.get("skip_button", (0, 0))[1],
                      (255, 255, 255))],
        click_coords=ELEMENT_COORDS.get("skip_button"),
    ),
    "recruitment_panel_indicator": UIElement(
        name="recruitment_panel_indicator",
        pixel_points=[(ELEMENT_COORDS.get("recruitment_panel_indicator", (0, 0))[0],
                      ELEMENT_COORDS.get("recruitment_panel_indicator", (0, 0))[1],
                      (255, 255, 255))],
    ),
    "refresh_button": UIElement(
        name="refresh_button",
        pixel_points=[(ELEMENT_COORDS.get("refresh_button", (0, 0))[0],
                      ELEMENT_COORDS.get("refresh_button", (0, 0))[1],
                      (0, 153, 220))],
        click_coords=ELEMENT_COORDS.get("refresh_button"),
    ),
    "confirm_recruitment_button": UIElement(
        name="confirm_recruitment_button",
        pixel_points=[(ELEMENT_COORDS.get("confirm_recruitment_button", (0, 0))[0],
                      ELEMENT_COORDS.get("confirm_recruitment_button", (0, 0))[1],
                      (0, 153, 220))],
        click_coords=ELEMENT_COORDS.get("confirm_recruitment_button"),
    ),
    "main_menu_indicator": UIElement(
        name="main_menu_indicator",
        pixel_points=[(ELEMENT_COORDS.get("main_menu_indicator", (0, 0))[0],
                      ELEMENT_COORDS.get("main_menu_indicator", (0, 0))[1],
                      (255, 255, 255))],
    ),
        # Back button (fill coords you use for back)
    "back_button": UIElement(
        name="back_button",
        pixel_points=[(0, 0, (49, 49, 49))],  # TODO: replace (0,0) with actual coords
        click_coords=None  # optional; if you prefer clicking instead of esc
    ),

    # Main menu confirmation group: use several bright white anchors
    "main_menu_confirm": UIElement(
        name="main_menu_confirm",
        pixel_points=[
            (1355, 110, (255, 255, 255)),   # existing indicator in your code
            (0, 0, (255, 255, 255)),        # TODO: replace with another reliable white anchor
            (0, 0, (255, 255, 255)),        # TODO: and one more
        ]
    ),

    # Optional named tiles to use with tap/safe_click (if you want)
    "tile_recruit": UIElement(name="tile_recruit", click_coords=(1500, 760)),
    "tile_base": UIElement(name="tile_base", click_coords=(1550, 950)),
}


def get_element(name: str) -> Optional[UIElement]:
    return ELEMENTS.get(name)


