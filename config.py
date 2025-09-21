import json
import os
from dataclasses import dataclass, asdict, replace
from typing import Tuple, List, Optional


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


# Logging configuration (levels as strings: DEBUG, INFO, WARNING, ERROR)
@dataclass(frozen=True)
class Logging:
    enabled: bool = True
    console_level: str = "INFO"
    file_level: str = "DEBUG"


# Gameplay/automation knobs for Arknights scenarios
@dataclass(frozen=True)
class ArknightsSettings:
    # Recruitment
    use_expedite: bool = False
    finish_on_recruitment: bool = True

    # Store
    store_based_on: List[str] = ("discount", "rarity")  # priority order
    store_rarity_priority: List[str] = (
        "extremely_rare_orange",
        "very_rare_pink",
        "rare_blue",
        "uncommon_yellow",
        "common_gray",
    )

    # Terminal / Orundum
    use_total_proxy: bool = True
    orundum_location: int = 1
    amount_orundum: int = 0
    amount_sanity: int = 174
    orundum_income: int = 330
    orundum_cap: int = 1800
    sanity_taken: int = 25


@dataclass(frozen=True)
class AnimationSettings:
    # General scramble effect duration (seconds)
    scramble_effect_duration: float = 1.2
    # Typewriter per-character delay (seconds)
    typewriter_speed: float = 0.035
    type_writer_fast: float = 0.06
    # Delay between dots in dotted sequences (seconds)
    dots_delay: float = 0.25
    # General status/notice dwell time (seconds)
    status_effect_duration: float = 1.2
    # Boot sequence specific
    welcome_speed: float = 0.02
    username_speed: float = 0.06
    prts_speed: float = 0.06
    per_char_scramble_duration: float = 0.25
    settled_color_delay: float = 0.05


@dataclass(frozen=True)
class UIColors:
    """Logical color scheme for the curses UI. Values are color names.

    Allowed names: 'black','red','green','yellow','blue','magenta','cyan','white','default'
    """
    border: str = 'cyan'
    title: str = 'yellow'
    on: str = 'green'
    off: str = 'red'
    text: str = 'white'
    selection_fg: str = 'white'
    selection_bg: str = 'blue'
    warning: str = 'white'  # window-not-found, etc.
    error: str = 'red'
    spinner: str = 'yellow'

# Keeping coordinates inside elements.py now; left here intentionally empty.
ELEMENT_COORDS = {}


class Settings:
    timeouts = Timeouts()
    colors = Colors()
    clicks = Clicks()
    safety = Safety()
    observability = Observability()
    logging = Logging()
    arknights = ArknightsSettings()
    animation = AnimationSettings()
    ui_colors = UIColors()


# --- Persistence helpers for user-tunable settings ---
_DEFAULT_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'user_settings.json')


def save_user_settings(path: Optional[str] = None) -> bool:
    try:
        p = path or _DEFAULT_SETTINGS_PATH
        data = {
            'logging': asdict(Settings.logging),
            'arknights': asdict(Settings.arknights),
            'animation': asdict(Settings.animation),
            'safety': asdict(Settings.safety),
            'observability': asdict(Settings.observability),
        }
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def load_user_settings(path: Optional[str] = None) -> bool:
    try:
        p = path or _DEFAULT_SETTINGS_PATH
        if not os.path.exists(p):
            return False
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'logging' in data:
            Settings.logging = replace(Settings.logging, **data['logging'])
        if 'arknights' in data:
            Settings.arknights = replace(Settings.arknights, **data['arknights'])
        if 'animation' in data:
            Settings.animation = replace(Settings.animation, **data['animation'])
        if 'safety' in data:
            Settings.safety = replace(Settings.safety, **data['safety'])
        if 'observability' in data:
            Settings.observability = replace(Settings.observability, **data['observability'])
        return True
    except Exception:
        return False


