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
            # (1348, 110, (255, 255, 255)), # Originium icon
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
    "terminal_indicator": UIElement(
        name="terminal_indicator",
        pixel_points=[
            (1508, 212, (255, 255, 255)), # white background of Rhodes logo - right side
            (1460, 210, (255, 255, 255)), # white background of Rhodos logo - left side
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
    # Recruitment tiles (centers)
    #TODO: Tweak coordinates to avoid overlapping of different checks
    "recruitment_tile_1": UIElement(name="recruitment_tile_1", pixel_points=[(486, 435, (255, 255, 255))], click_coords=(486, 435)),
    "recruitment_tile_2": UIElement(name="recruitment_tile_2", pixel_points=[(1433, 435, (255, 255, 255))], click_coords=(1433, 435)),
    "recruitment_tile_3": UIElement(name="recruitment_tile_3", pixel_points=[(486, 851, (255, 255, 255))], click_coords=(486, 851)),
    "recruitment_tile_4": UIElement(name="recruitment_tile_4", pixel_points=[(1433, 851, (255, 255, 255))], click_coords=(1433, 851)),

    # Recruitment tags indicators
    "recruitment_tag_1": UIElement(name="recruitment_tag_1", pixel_points=[(763, 578, (49, 49, 49))], click_coords=(763, 578)),
    "recruitment_tag_2": UIElement(name="recruitment_tag_2", pixel_points=[(1019, 575, (49, 49, 49))], click_coords=(1019, 575)),
    "recruitment_tag_3": UIElement(name="recruitment_tag_3", pixel_points=[(1269, 576, (49, 49, 49))], click_coords=(1269, 576)),
    "recruitment_tag_4": UIElement(name="recruitment_tag_4", pixel_points=[(767, 684, (49, 49, 49))], click_coords=(767, 684)),
    "recruitment_tag_5": UIElement(name="recruitment_tag_5", pixel_points=[(1015, 681, (49, 49, 49))], click_coords=(1015, 681)),

    # Recruitment permit check offset from tile center: (tile.x-105, tile.y+25)
    "recruitment_permit_1": UIElement(name="recruitment_permit_1", pixel_points=[(381, 460, (255, 255, 255))], click_coords=(381, 460)),
    "recruitment_permit_2": UIElement(name="recruitment_permit_2", pixel_points=[(1328, 460, (255, 255, 255))], click_coords=(1328, 460)),
    "recruitment_permit_3": UIElement(name="recruitment_permit_3", pixel_points=[(381, 876, (255, 255, 255))], click_coords=(381, 876)),
    "recruitment_permit_4": UIElement(name="recruitment_permit_4", pixel_points=[(1328, 876, (255, 255, 255))], click_coords=(1328, 876)),
    
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

    # Recruitment flow buttons/points
    "recruit_refresh_button": UIElement(
        name="recruit_refresh_button",
        pixel_points=[(1450, 604, (0, 153, 220))],
        click_coords=(1450, 604),
    ),
    "recruitment_panel_indicator": UIElement(
        name="recruitment_panel_indicator",
        pixel_points=[
            (1460, 860, (255, 255, 255)),
            (1460, 955, (255, 255, 255)),
            (580, 460, (49, 49, 49)),
            ],
        click_coords=(1460, 860),
    ),
    "recruit_refresh_confirm": UIElement(
        name="recruit_refresh_confirm",
        pixel_points=[(1260, 727, (255, 255, 255))],
        click_coords=(1260, 727),
    ),
    "recruit_confirm_button_top": UIElement(
        name="recruit_confirm_button_top",
        pixel_points=[(674, 449, (0, 0, 0))],
        click_coords=(674, 449),
    ),
    "recruit_confirm_button_bottom": UIElement(
        name="recruit_confirm_button_bottom",
        pixel_points=[(1463, 876, (0, 153, 220))],
        click_coords=(1463, 876),
    ),
    "recruit_confirm_state_pixel": UIElement(
        name="recruit_confirm_state_pixel",
        pixel_points=[(1539, 865, (0, 153, 220))],
        click_coords=(1539, 865),
    ),
    "recruit_close_panel_button": UIElement(
        name="recruit_close_panel_button",
        pixel_points=[(1461, 955, (255, 255, 255))],
        click_coords=(1461, 955),
    ),
    # Hiring tile click positions per tile (center + 136 on Y)
    "hiring_tile_1": UIElement(name="hiring_tile_1", click_coords=(486, 571)),
    "hiring_tile_2": UIElement(name="hiring_tile_2", click_coords=(1433, 571)),
    "hiring_tile_3": UIElement(name="hiring_tile_3", click_coords=(486, 987)),
    "hiring_tile_4": UIElement(name="hiring_tile_4", click_coords=(1433, 987)),
    # Expedite button per tile (tile.x+220, tile.y+145)
    "expedite_button_1": UIElement(name="expedite_button_1", click_coords=(706, 580)),
    "expedite_button_2": UIElement(name="expedite_button_2", click_coords=(1653, 580)),
    "expedite_button_3": UIElement(name="expedite_button_3", click_coords=(706, 996)),
    "expedite_button_4": UIElement(name="expedite_button_4", click_coords=(1653, 996)),
    "expedite_confirm": UIElement(
        name="expedite_confirm",
        pixel_points=[(1432, 748, (255, 255, 255))],
        click_coords=(1432, 748),
    ),
    # Skip button and post-skip wait points
    "skip_button_anchor": UIElement(name="skip_button_anchor", pixel_points=[(1833, 51, (255, 255, 255))], click_coords=(1833, 51)),
    "post_skip_wait_point": UIElement(name="post_skip_wait_point", pixel_points=[(847, 120, (255, 255, 255))], click_coords=(847, 120)),
    "skip_end_indicator": UIElement(name="skip_end_indicator", pixel_points=[(1717, 52, (255, 255, 255))], click_coords=(1717, 52)),
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
        name="orundum_location_switch_button",
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
    "mission_non_proxy_complete_screen": UIElement(
        name="mission_non_proxy_complete_screen",
        pixel_points=[(208, 386, (255, 255, 255))],
        click_coords=(208, 386),
    ),
}


def get_element(name: str) -> Optional[UIElement]:
    return ELEMENTS.get(name)


