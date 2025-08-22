from dataclasses import dataclass
from typing import Tuple


# Global configuration for automation behavior. Adjust values as needed.


@dataclass(frozen=True)
class Timeouts:
    default_timeout: float = 10.0
    short_timeout: float = 5.0
    long_timeout: float = 30.0
    check_interval_min: float = 0.05
    check_interval_max: float = 0.15
    stability_frames: int = 2  # require N consecutive confirmations


@dataclass(frozen=True)
class Colors:
    # Default color matching confidence (0..1). 1.0 means exact match
    default_confidence: float = 0.95
    # ROI sampling size for more robust color checks
    roi_half_size: int = 2  # 2 => 5x5 window


@dataclass(frozen=True)
class Clicks:
    jitter_radius_px: int = 3  # randomize click within this radius
    post_click_grace_ms: int = 80  # short grace after click


@dataclass(frozen=True)
class Safety:
    dry_run: bool = False  # if True, do not actually click; only log
    enable_panic_key: bool = True
    panic_key: str = "f8"  # best-effort; requires optional 'keyboard' package


@dataclass(frozen=True)
class Observability:
    enable_failure_screenshots: bool = True
    artifacts_dir_name: str = "logs"  # store alongside existing logs
    # rectangle color for ROI annotations (BGR as used by cv2 drawing)
    annotation_color_bgr: Tuple[int, int, int] = (0, 165, 255)  # orange
    annotation_thickness_px: int = 2


# Named coordinates and regions used by ergonomic APIs and states.
# Fill in or adjust as needed for your setup.
ELEMENT_COORDS = {
    # Examples prefilled based on current scenarios. Adjust if needed.
    "skip_button": (1833, 51),
    "recruitment_panel_indicator": (1225, 28),
    "refresh_button": (1450, 604),
    "confirm_recruitment_button": (1463, 876),
    "main_menu_indicator": (1355, 110),
    "back_button": (130, 50),
    # Main menu tiles (migrated from MainMenu.tile_coords)
    "tile_recruit": (1500, 760),
    "tile_headhunt": (1760, 760),
    "tile_store": (1300, 720),
    "tile_missions": (1200, 900),
    "tile_base": (1550, 950),
    "tile_terminal": (1450, 250),
    "tile_friends": (540, 850),
}


class Settings:
    timeouts = Timeouts()
    colors = Colors()
    clicks = Clicks()
    safety = Safety()
    observability = Observability()


