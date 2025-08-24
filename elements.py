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
    "back_button": UIElement(
        name="back_button",
        pixel_points=[(ELEMENT_COORDS.get("back_button", (0, 0))[0],
                      ELEMENT_COORDS.get("back_button", (0, 0))[1],
                      (49, 49, 49))],
        click_coords=ELEMENT_COORDS.get("back_button"),
    ),
    # Indicators
    "main_menu_indicators": UIElement(
        name="main_menu_indicators",
        pixel_points=[
            (1355, 110, (255, 255, 255)), # Originium icon
            (69, 78, (255, 255, 255)), # Settings icon
            (160, 75, (255, 255, 255)), # Info icon
            (290, 75, (255, 255, 255)), # Mail icon
        ]
    ),
    "recruitment_indicator": UIElement(
        name="recruitment_indicator",
        pixel_points=[(ELEMENT_COORDS.get("recruitment_indicator", (0, 0))[0],
                      ELEMENT_COORDS.get("recruitment_indicator", (0, 0))[1],
                      (255, 255, 255))],
    ),
    "base_indicator": UIElement(
        name="base_indicator",
        pixel_points=[(ELEMENT_COORDS.get("base_indicator", (0, 0))[0],
                      ELEMENT_COORDS.get("base_indicator", (0, 0))[1],
                      (255, 255, 255))],
    ),
    # Optional named tiles to use with tap/safe_click (click-only; no pixel checks)
    "tile_recruit": UIElement(name="tile_recruit", click_coords=ELEMENT_COORDS.get("tile_recruit")),
    "tile_headhunt": UIElement(name="tile_headhunt", click_coords=ELEMENT_COORDS.get("tile_headhunt")),
    "tile_store": UIElement(name="tile_store", click_coords=ELEMENT_COORDS.get("tile_store")),
    "tile_missions": UIElement(name="tile_missions", click_coords=ELEMENT_COORDS.get("tile_missions")),
    "tile_base": UIElement(name="tile_base", click_coords=ELEMENT_COORDS.get("tile_base")),
    "tile_terminal": UIElement(name="tile_terminal", click_coords=ELEMENT_COORDS.get("tile_terminal")),
    "tile_friends": UIElement(name="tile_friends", click_coords=ELEMENT_COORDS.get("tile_friends")),
    
    # Base notification elements (click-only; position determined by color check)
    "notification_upper": UIElement(name="notification_upper", click_coords=ELEMENT_COORDS.get("notification_upper")),
    "notification_lower": UIElement(name="notification_lower", click_coords=ELEMENT_COORDS.get("notification_lower")),
    "notification_color_check": UIElement(name="notification_color_check", click_coords=ELEMENT_COORDS.get("notification_color_check")),
    "base_factory_1": UIElement(
        name="base_factory_1", 
        pixel_points=[(*ELEMENT_COORDS.get("base_factory_1"), (255, 216, 2))],
        click_coords=ELEMENT_COORDS.get("base_factory_1"),
    ),
    "base_factory_2": UIElement(
        name="base_factory_2", 
        pixel_points=[(*ELEMENT_COORDS.get("base_factory_2"), (255, 216, 2))],
        click_coords=ELEMENT_COORDS.get("base_factory_2"),
    ),
    "base_factory_3": UIElement(
        name="base_factory_3", 
        pixel_points=[(*ELEMENT_COORDS.get("base_factory_3"), (255, 216, 2))],
        click_coords=ELEMENT_COORDS.get("base_factory_3"),
    ),
    "base_factory_4": UIElement(
        name="base_factory_4", 
        pixel_points=[(*ELEMENT_COORDS.get("base_factory_4"), (255, 216, 2))],
        click_coords=ELEMENT_COORDS.get("base_factory_4"),
    ),
}


def get_element(name: str) -> Optional[UIElement]:
    return ELEMENTS.get(name)


