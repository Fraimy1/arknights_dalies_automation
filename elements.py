from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


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
        pixel_points=[(1833, 51, (255, 255, 255))],
        click_coords=(1833, 51),
    ),

    "refresh_button": UIElement(
        name="refresh_button",
        pixel_points=[(1450, 604, (0, 153, 220))],
        click_coords=(1450, 604),
    ),
    "confirm_recruitment_button": UIElement(
        name="confirm_recruitment_button",
        pixel_points=[(1463, 876, (0, 153, 220))],
        click_coords=(1463, 876),
    ),
    "back_button": UIElement(
        name="back_button",
        pixel_points=[(130, 50, (49, 49, 49))],
        click_coords=(130, 50),
    ),
    # Indicators
    "main_menu_indicators": UIElement(
        name="main_menu_indicators",
        pixel_points=[
            (1366, 110, (255, 255, 255)), # Originium icon
            (69, 78, (255, 255, 255)), # Settings icon
            (160, 75, (255, 255, 255)), # Info icon
            (290, 75, (255, 255, 255)), # Mail icon
        ]
    ),
    "recruitment_indicator": UIElement(
        name="recruitment_indicator",
        pixel_points=[(1225, 28, (255, 255, 255))],
    ),
    "base_indicator": UIElement(
        name="base_indicator",
        pixel_points=[(270, 168, (255, 255, 255))],
    ),
    "missions_indicators": UIElement(
        name="missions_indicators",
        pixel_points=[
            (1280, 30, (225, 225, 225)), # Weeklymission
            (720, 30, (49, 49, 49)), # Daily missions
            (1860, 70, (225, 225, 225)), # Campaign missions
        ],
    ),
    # Optional named tiles to use with tap/safe_click (click-only; no pixel checks)
    "tile_recruit": UIElement(name="tile_recruit", click_coords=(1500, 760)),
    "tile_headhunt": UIElement(name="tile_headhunt", click_coords=(1760, 760)),
    "tile_store": UIElement(name="tile_store", click_coords=(1300, 720)),
    "tile_missions": UIElement(name="tile_missions", click_coords=(1200, 900)),
    "tile_base": UIElement(name="tile_base", click_coords=(1550, 950)),
    "tile_terminal": UIElement(name="tile_terminal", click_coords=(1450, 250)),
    "tile_friends": UIElement(name="tile_friends", click_coords=(540, 850)),
    
    # Base notification elements (click-only; position determined by color check)
    "notification_upper": UIElement(name="notification_upper", click_coords=(1802, 140)),
    "notification_lower": UIElement(name="notification_lower", click_coords=(1802, 207)),
    "notification_color_check": UIElement(name="notification_color_check", click_coords=(1828, 115)),
    "base_factory_1": UIElement(
        name="base_factory_1", 
        pixel_points=[(586, 452, (255, 216, 2))],
        click_coords=(586, 452),
    ),
    "base_factory_2": UIElement(
        name="base_factory_2", 
        pixel_points=[(246, 564, (255, 216, 2))],
        click_coords=(246, 564),
    ),
    "base_factory_3": UIElement(
        name="base_factory_3", 
        pixel_points=[(700, 564, (255, 216, 2))],
        click_coords=(700, 564),
    ),
    "base_factory_4": UIElement(
        name="base_factory_4", 
        pixel_points=[(361, 678, (255, 216, 2))],
        click_coords=(361, 678),
    ),
    # Missions
    "mission_collect_all_button": UIElement(
        name="mission_collect_all_button",
        pixel_points=[(1508, 210, (0, 152, 220))],
        click_coords=(1508, 210),
    ),
    "weekly_mission_button": UIElement(
        name="weekly_mission_button",
        pixel_points=[(1280, 30, (255, 255, 255))],
        click_coords=(1280, 30),
    ),
}


def get_element(name: str) -> Optional[UIElement]:
    return ELEMENTS.get(name)


