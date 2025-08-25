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
    'confirm_button': UIElement(
        name="confirm_button",
        pixel_points=[(1260, 727, (255, 255, 255))],
        click_coords=(1260, 727),
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
    "friends_indicator": UIElement(
        name="friends_indicator",
        pixel_points=[(100, 345, (255, 255, 255))],
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
    # Friends
    "friends_menu": UIElement(
        name="friends_menu",
        pixel_points=[(100, 345, (255, 255, 255))],
        click_coords=(100, 345),
    ),
    "friend_tile": UIElement(
        name="friend_tile",
        pixel_points=None,
        click_coords=(1623, 260),
    ),
    "next_button": UIElement(
        name="next_button",
        pixel_points=[(1645, 68, (111, 37, 0))],
        click_coords=(1800, 943),
    ),
    # Orundum farming
    "orundum_menu_button": UIElement(
        name="orundum_menu_button",
        pixel_points=[(1600, 210, (200, 42, 54))],
        click_coords=(1600, 210),
    ),
    "orundum_location_switch_button": UIElement(
        name="orundum_location_switch",
        pixel_points=[(1690, 1000, (0, 0, 0))],
        click_coords=(1690, 1000),
    ),
    "orundum_current_mission": UIElement(
        name="orundum_current_mission",
        pixel_points=[(1350, 144, (255, 255, 255))],
        click_coords=(1350, 144),
    ),
    "orundum_permanent_mission_1": UIElement(
        name="orundum_permanent_mission_1",
        pixel_points=[(1350, 366, (255, 255, 255))],
        click_coords=(1349, 366),
    ),
    "orundum_permanent_mission_2": UIElement(
        name="orundum_permanent_mission_2",
        pixel_points=[(1350, 517, (255, 255, 255))],
        click_coords=(1347, 517),
    ),
    "orundum_permanent_mission_3": UIElement(
        name="orundum_permanent_mission_3",
        pixel_points=[(1350, 669, (255, 255, 255))],
        click_coords=(1349, 669),
    ),
    "auto_deploy_button": UIElement(
        name="auto_deploy_button",
        pixel_points=[(1600, 886, (255, 255, 255))],
        click_coords=(1600, 886),
    ),
    "total_proxy_available": UIElement(
        name="total_proxy_available",
        pixel_points=[(1436, 886, (66, 198, 255))],
        click_coords=(1436, 886),
    ),
    "start_button": UIElement(
        name="start_button",
        pixel_points=[(1775, 1025, (35, 35, 35))],
        click_coords=(1775, 1025),
    ),
    "mission_start_button": UIElement(
        name="mission_start_button",
        pixel_points=[(1340, 70, (255, 255, 255))],
        click_coords=(1735, 950),
    ),
    "mission_complete_screen": UIElement(
        name="mission_complete_screen",
        pixel_points=[
            (20, 340, (76, 76, 76)),
            (20, 465, (76, 76, 76)), 
            (100, 455, (0, 0, 0))
        ], # Rhodes Island logo
        click_coords=(100, 455),
    ),
    # #! Positions of orundum region on the screen change every 2-4 weeks
    # "orundum_region_yan_lungmen": UIElement(
    #     name="orundum_region_yan_lungmen",
    #     pixel_points=None,
    #     click_coords=(300, 375),
    # ),
    # "orundum_lungmen_outskirts": UIElement(
    #     name="orundum_lungmen_outskirts",
    #     pixel_points=None,
    #     click_coords=(700,600),
    # )
}


def get_element(name: str) -> Optional[UIElement]:
    return ELEMENTS.get(name)


