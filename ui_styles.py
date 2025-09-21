from typing import Dict, Any

# Central, per-element style map (a CSS-like theme sheet).
# All colors are logical names; runtime maps them to curses colors.

from config import Settings


STYLES: Dict[str, Dict[str, Any]] = {
    # --- Global / tokens ---
    "border": {
        "color": Settings.ui_colors.border,
        "box_chars": {"horiz": "─", "vert": "│", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘"},
    },
    "text_default": {"color": Settings.ui_colors.text},
    "title_default": {"color": Settings.ui_colors.title, "bold": True},
    "on_value": {"color": Settings.ui_colors.on, "bold": True},
    "off_value": {"color": Settings.ui_colors.off, "bold": True},
    "selection": {"fg": Settings.ui_colors.selection_fg, "bg": Settings.ui_colors.selection_bg, "bold": True},
    "warning_text": {"color": Settings.ui_colors.warning, "bold": True},
    "error_text": {"color": Settings.ui_colors.error, "bold": True},

    # --- Header ---
    # Title split into "PRTS" word and the rest
    "title_prts": {
        "color": Settings.ui_colors.text,
        "bold": True,
        "type_speed": Settings.animation.prts_speed,
        "per_char_scramble_duration": Settings.animation.per_char_scramble_duration,
        "settled_green": False,
        "settled_color": Settings.ui_colors.text,
    },
    "title_rest": {
        "color": Settings.ui_colors.title,
        "bold": True,
        "type_speed": Settings.animation.type_writer_fast,
        "per_char_scramble_duration": Settings.animation.per_char_scramble_duration,
        "settled_green": False,
        "settled_color": Settings.ui_colors.title,
    },
    "clock": {"color": Settings.ui_colors.text, "bold": True},

    # --- Window status panel ---
    "status_panel_border": {"color": Settings.ui_colors.border},
    "status_panel_title": {"color": Settings.ui_colors.title, "bold": True},
    "status_position": {"color": Settings.ui_colors.text},
    "status_resolution": {"color": Settings.ui_colors.text},
    "status_warning": {"color": Settings.ui_colors.warning, "bold": True, "text_prefix": "Warning: "},

    # --- Operations menu ---
    "menu_item": {"color": Settings.ui_colors.text},
    "menu_item_selected": {"fg": Settings.ui_colors.selection_fg, "bg": Settings.ui_colors.selection_bg, "bold": True},

    # --- Footer ---
    "footer": {"color": Settings.ui_colors.border},

    # --- Toasts ---
    "toast_info": {"color": Settings.ui_colors.text, "duration": max(4.0, Settings.animation.status_effect_duration)},
    "toast_warning": {"color": Settings.ui_colors.off, "duration": max(4.0, Settings.animation.status_effect_duration)},
    "toast_error": {"color": Settings.ui_colors.error, "duration": max(4.0, Settings.animation.status_effect_duration)},

    # --- PRTS System Settings ---
    "settings_header": {"color": Settings.ui_colors.title, "bold": True},
    "settings_label": {"color": Settings.ui_colors.text},
    "settings_value_on": {"color": Settings.ui_colors.on, "bold": True},
    "settings_value_off": {"color": Settings.ui_colors.off, "bold": True},
    "settings_hint": {"color": Settings.ui_colors.border},

    # --- Automation Settings (grouped sections) ---
    "auto_section_header": {"color": Settings.ui_colors.title, "bold": True},
    "auto_label": {"color": Settings.ui_colors.text},
    "auto_value_list": {"color": Settings.ui_colors.text},
    "auto_value_on": {"color": Settings.ui_colors.on, "bold": True},
    "auto_value_off": {"color": Settings.ui_colors.off, "bold": True},
    "auto_hint": {"color": Settings.ui_colors.border},
    "auto_wrap_continuation_prefix": {"text": "   "},

    # --- Boot / Welcome sequence ---
    "welcome_message": {
        # "Welcome " prefix
        "color": Settings.ui_colors.title,
        "bold": True,
        "type_speed": Settings.animation.welcome_speed,
        "per_char_scramble_duration": max(0.05, Settings.animation.per_char_scramble_duration / 2),
        "settled_green": False,
    },
    "welcome_message_username": {
        # Username e.g. "Oracle"
        "color": Settings.ui_colors.text,
        "bold": True,
        "type_speed": Settings.animation.username_speed,
        "per_char_scramble_duration": Settings.animation.per_char_scramble_duration,
        "settled_green": True,
        "settled_color": Settings.ui_colors.text,
    },
    "boot_admin_label": {"color": Settings.ui_colors.text, "bold": True, "type_speed": Settings.animation.typewriter_speed},
    "boot_dots": {"color": Settings.ui_colors.text, "dots_delay": Settings.animation.dots_delay},
    "boot_on_value": {"color": Settings.ui_colors.on, "bold": True, "per_char_scramble_duration": Settings.animation.per_char_scramble_duration, "settled_color": Settings.ui_colors.on},
    "boot_terminal_label": {"color": Settings.ui_colors.text, "type_speed": Settings.animation.typewriter_speed},
    "boot_terminal_status": {"color": Settings.ui_colors.on, "bold": True, "per_char_scramble_duration": Settings.animation.per_char_scramble_duration, "settled_color": Settings.ui_colors.on},
    "boot_security_label": {"color": Settings.ui_colors.text, "type_speed": Settings.animation.typewriter_speed},
    "boot_security_level": {"color": Settings.ui_colors.title, "bold": True, "per_char_scramble_duration": Settings.animation.per_char_scramble_duration, "settled_color": Settings.ui_colors.title},
    "spinner": {"color": Settings.ui_colors.title, "frame_delay": 0.1, "frames": ["⠋","⠙","⠸","⠴","⠦","⠇"]},

    # --- Reusable tokens ---
    "prts_word": {"color": Settings.ui_colors.title, "bold": True, "type_speed": Settings.animation.prts_speed},
}


