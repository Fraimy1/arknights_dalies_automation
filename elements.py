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
    "back_button": UIElement(
        name="back_button",
        pixel_points=[(ELEMENT_COORDS.get("back_button", (0, 0))[0],
                      ELEMENT_COORDS.get("back_button", (0, 0))[1],
                      (49, 49, 49))],
        click_coords=ELEMENT_COORDS.get("back_button"),
    ),
    "main_menu_confirm_points": UIElement(
        name="main_menu_confirm_points",
        pixel_points=[
            (1355, 110, (255, 255, 255)), # Originium icon
            (69, 78, (255, 255, 255)), # Settings icon
            (160, 75, (255, 255, 255)), # Info icon
            (290, 75, (255, 255, 255)), # Mail icon
        ]
    ),

    # Optional named tiles to use with tap/safe_click (click-only; no pixel checks)
    "tile_recruit": UIElement(name="tile_recruit", click_coords=ELEMENT_COORDS.get("tile_recruit")),
    "tile_headhunt": UIElement(name="tile_headhunt", click_coords=ELEMENT_COORDS.get("tile_headhunt")),
    "tile_store": UIElement(name="tile_store", click_coords=ELEMENT_COORDS.get("tile_store")),
    "tile_missions": UIElement(name="tile_missions", click_coords=ELEMENT_COORDS.get("tile_missions")),
    "tile_base": UIElement(name="tile_base", click_coords=ELEMENT_COORDS.get("tile_base")),
    "tile_terminal": UIElement(name="tile_terminal", click_coords=ELEMENT_COORDS.get("tile_terminal")),
    "tile_friends": UIElement(name="tile_friends", click_coords=ELEMENT_COORDS.get("tile_friends")),
}


def get_element(name: str) -> Optional[UIElement]:
    return ELEMENTS.get(name)


