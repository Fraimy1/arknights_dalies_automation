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


# Keeping coordinates inside elements.py now; left here intentionally empty.
ELEMENT_COORDS = {}


class Settings:
    timeouts = Timeouts()
    colors = Colors()
    clicks = Clicks()
    safety = Safety()
    observability = Observability()


