import curses
import locale
import random
import time
from dataclasses import replace
from typing import List, Tuple

from logger import (
    logger,
    set_console_level,
    get_console_level,
    set_logging_enabled,
)
from utils import ark_window
from config import Settings, save_user_settings, load_user_settings
from scenarios import TaskAggregator, MainMenu
from ui_styles import STYLES


locale.setlocale(locale.LC_ALL, '')


PRTS_TITLE_PART1 = "PRTS"
PRTS_TITLE_PART2 = " Task Automation Project"
FOOTER = "// Connection to Rhodes Island PRTS system established //"


class PRTSInterface:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.selected_index = 0
        self.view = 'menu'  # 'menu' | 'settings' | 'automation'
        self.settings_index = 0
        self.did_scramble_title = False
        self.automation_index = 0
        self._toast = None  # {'text': str, 'level': 'info'|'warning'|'error', 'expires': float}

        # Menu entries (keyboard: arrows or number keys)
        self.menu_items: List[Tuple[str, str]] = [
            ("Run All Dailies", "run_all"),
            ("Recruitment Dailies", "recruit"),
            ("Base Dailies", "base"),
            ("Friends Dailies", "friends"),
            ("Store Dailies", "store"),
            ("Missions Dailies", "missions"),
            ("Terminal Dailies", "terminal"),
            ("Return to Main Menu", "return_menu"),
            ("PRTS System Settings", "settings"),
            ("Automation Settings", "automation"),
            ("Quit", "quit"),
        ]

        # Settings items: (label, path)
        # We reassign whole dataclass instances via dataclasses.replace to bypass frozen fields
        self.settings_items: List[Tuple[str, str]] = [
            ("Dry Run Mode", "safety.dry_run"),
            ("Failure Artifacts", "observability.enable_failure_screenshots"),
            ("Enable Panic Key", "safety.enable_panic_key"),
            ("Console Log Level", "logging.console_level"),
            ("Logging Output", "logging.enabled"),
        ]

        # Automation settings grouped by blocks
        self.automation_sections: List[Tuple[str, List[Tuple[str, str]]]] = [
            ("Recruitment", [
                ("Use Expedite (Recruitment)", "arknights.use_expedite"),
                ("Finish On Recruitment", "arknights.finish_on_recruitment"),
            ]),
            ("Terminal", [
                ("Use Total Proxy", "arknights.use_total_proxy"),
            ]),
            ("Credit Store", [
                ("Purchase Order", "arknights.store_based_on"),
                ("Rarity Priority", "arknights.store_rarity_priority"),
            ]),
        ]

    def _automation_flat_items(self) -> List[Tuple[str, str]]:
        flat: List[Tuple[str, str]] = []
        for _, items in self.automation_sections:
            flat.extend(items)
        return flat

    # --- Draw helpers ---
    def _init_colors(self):
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        # Map logical colors from config to curses
        def c(name: str) -> int:
            name = (name or 'default').lower()
            return {
                'black': curses.COLOR_BLACK,
                'red': curses.COLOR_RED,
                'green': curses.COLOR_GREEN,
                'yellow': curses.COLOR_YELLOW,
                'blue': curses.COLOR_BLUE,
                'magenta': curses.COLOR_MAGENTA,
                'cyan': curses.COLOR_CYAN,
                'white': curses.COLOR_WHITE,
                'default': -1,
            }.get(name, -1)

        ui = Settings.ui_colors
        # Pairs
        curses.init_pair(1, c(ui.border), -1)    # borders
        curses.init_pair(2, c(ui.title), -1)     # title
        curses.init_pair(3, c(ui.on), -1)        # ON
        curses.init_pair(4, c(ui.off), -1)       # OFF
        curses.init_pair(5, c(ui.selection_fg), c(ui.selection_bg))  # selection
        curses.init_pair(6, c(ui.text), -1)      # normal text

    # Style helpers
    def _pair_for_color(self, color_name: str) -> int:
        uic = Settings.ui_colors
        if color_name == uic.border:
            return 1
        if color_name == uic.title:
            return 2
        if color_name == uic.on:
            return 3
        if color_name in (uic.off, uic.error):
            return 4
        if color_name == uic.text:
            return 6
        if color_name == uic.selection_fg:
            return 5
        if color_name == uic.warning:
            return 6  # warning uses text color
        return 6  # default to text color

    def _attr_from_style(self, key: str, selection: bool = False) -> int:
        st = STYLES.get(key, {})
        if selection:
            attr = curses.color_pair(5)
        else:
            color = st.get('color', Settings.ui_colors.text)
            attr = curses.color_pair(self._pair_for_color(color))
        if st.get('bold'):
            attr |= curses.A_BOLD
        return attr

    def _scramble(self, y: int, x: int, text: str, color_pair: int = 2, duration: float = None, per_char: bool = True, settled_green: bool = False, speed: float = None, per_char_duration: float = None, settled_color_pair: int = None):
        """Per-character scramble typing effect.

        - Characters appear sequentially.
        - Each character flickers in white, then settles to target.
        - If settled_green=True, settled characters render in green (pair 3).
        """
        if duration is None:
            duration = Settings.animation.scramble_effect_duration
        if speed is None:
            speed = Settings.animation.typewriter_speed
        if per_char_duration is None:
            per_char_duration = Settings.animation.per_char_scramble_duration

        charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/|~#*+-"
        settle_delay = max(0.0, Settings.animation.settled_color_delay)

        cx = x
        for ch in text:
            if ch == ' ':
                try:
                    self.stdscr.addstr(y, cx, ' ', curses.color_pair(color_pair))
                    self.stdscr.refresh()
                except Exception:
                    pass
                cx += 1
                time.sleep(speed)
                continue

            t0 = time.time()
            # Flicker in white until per_char_duration elapsed
            while time.time() - t0 < per_char_duration:
                flick = random.choice(charset)
                try:
                    self.stdscr.addstr(y, cx, flick, curses.color_pair(6) | curses.A_BOLD)
                    self.stdscr.refresh()
                except Exception:
                    pass
                time.sleep(max(0.008, speed / 2))

            # Settle to actual char
            try:
                if settled_green:
                    pair = settled_color_pair if settled_color_pair is not None else 3
                    self.stdscr.addstr(y, cx, ch, curses.color_pair(pair) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, cx, ch, curses.color_pair(color_pair) | curses.A_BOLD)
                self.stdscr.refresh()
            except Exception:
                pass
            time.sleep(settle_delay)
            cx += 1

    def _typewriter(self, y: int, x: int, text: str, color_pair: int = 6, bold: bool = False):
        delay = max(0.001, Settings.animation.typewriter_speed)
        attr = curses.color_pair(color_pair) | (curses.A_BOLD if bold else 0)
        for i, ch in enumerate(text):
            try:
                self.stdscr.addstr(y, x + i, ch, attr)
                self.stdscr.refresh()
            except Exception:
                pass
            time.sleep(delay)

    def _dots(self, y: int, x: int, count: int = 3, color_pair: int = 6, delay: float = None):
        delay = max(0.001, Settings.animation.dots_delay if delay is None else delay)
        for i in range(1, count + 1):
            try:
                self.stdscr.addstr(y, x, '.' * i, curses.color_pair(color_pair))
                self.stdscr.refresh()
            except Exception:
                pass
            time.sleep(delay)

    def _spinner(self, y: int, x: int, duration: float = None):
        if duration is None:
            duration = Settings.animation.status_effect_duration
        s = STYLES.get('spinner', {})
        frames = s.get('frames', ['⠋','⠙','⠸','⠴','⠦','⠇'])
        frame_delay = float(s.get('frame_delay', 0.1))
        color_pair = self._pair_for_color(s.get('color', Settings.ui_colors.title))
        t0 = time.time()
        i = 0
        while time.time() - t0 < duration:
            try:
                self.stdscr.addstr(y, x, frames[i % len(frames)], curses.color_pair(color_pair))
                self.stdscr.refresh()
            except Exception:
                pass
            time.sleep(frame_delay)
            i += 1

    def _boot_sequence(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.erase()
        self._draw_borders()
        # Welcome header
        name = "Oracle"
        welcome = "Welcome "
        y = max(3, h // 3)
        x = max(2, (w - (len(welcome) + len(name))) // 2)
        # Welcome (fast) using style map
        ws = STYLES.get('welcome_message', {})
        self._scramble(
            y,
            x,
            welcome,
            color_pair=self._pair_for_color(ws.get('color', Settings.ui_colors.title)),
            speed=ws.get('type_speed', Settings.animation.welcome_speed),
            per_char_duration=ws.get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration / 2),
            settled_green=ws.get('settled_green', False),
            settled_color_pair=self._pair_for_color(ws.get('settled_color', Settings.ui_colors.title)),
        )
        # Username (slower per-char flicker, then green)
        us = STYLES.get('welcome_message_username', {})
        self._scramble(
            y,
            x + len(welcome),
            name,
            color_pair=self._pair_for_color(us.get('color', Settings.ui_colors.title)),
            speed=us.get('type_speed', Settings.animation.username_speed),
            per_char_duration=us.get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration),
            settled_green=us.get('settled_green', True),
            settled_color_pair=self._pair_for_color(us.get('settled_color', Settings.ui_colors.title)),
        )

        # Boot messages
        line_y = y + 3
        # 1) Administrator Privileges ... ON
        msg = "Administrator Privileges"
        self._typewriter(line_y, x, msg, color_pair=self._pair_for_color(STYLES.get('boot_admin_label', {}).get('color', Settings.ui_colors.text)), bold=STYLES.get('boot_admin_label', {}).get('bold', True))
        self._typewriter(line_y, x + len(msg) + 1, " ", color_pair=6)
        self._dots(
            line_y,
            x + len(msg) + 1,
            color_pair=self._pair_for_color(STYLES.get('boot_dots', {}).get('color', Settings.ui_colors.text)),
            delay=STYLES.get('boot_dots', {}).get('dots_delay', Settings.animation.dots_delay),
        )
        on_text = "ON"
        self._scramble(
            line_y,
            x + len(msg) + 1,
            on_text,
            color_pair=self._pair_for_color(STYLES.get('boot_on_value', {}).get('color', Settings.ui_colors.on)),
            per_char_duration=STYLES.get('boot_on_value', {}).get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration),
            settled_green=True,
            settled_color_pair=self._pair_for_color(STYLES.get('boot_on_value', {}).get('settled_color', Settings.ui_colors.on)),
        )
        line_y += 2

        # 2) Rhodes Island Terminal Link: STABLE
        msg2 = "Rhodes Island Terminal Link: "
        self._typewriter(line_y, x, msg2, color_pair=self._pair_for_color(STYLES.get('boot_terminal_label', {}).get('color', Settings.ui_colors.text)))
        self._scramble(
            line_y,
            x + len(msg2),
            "STABLE",
            color_pair=self._pair_for_color(STYLES.get('boot_terminal_status', {}).get('color', Settings.ui_colors.on)),
            per_char_duration=STYLES.get('boot_terminal_status', {}).get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration),
            settled_green=True,
            settled_color_pair=self._pair_for_color(STYLES.get('boot_terminal_status', {}).get('settled_color', Settings.ui_colors.on)),
        )
        line_y += 2

        # 3) Security Clearance Level: 3
        msg3 = "Security Clearance Level: "
        self._typewriter(line_y, x, msg3, color_pair=self._pair_for_color(STYLES.get('boot_security_label', {}).get('color', Settings.ui_colors.text)))
        self._scramble(
            line_y,
            x + len(msg3),
            "3",
            color_pair=self._pair_for_color(STYLES.get('boot_security_level', {}).get('color', Settings.ui_colors.title)),
            per_char_duration=STYLES.get('boot_security_level', {}).get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration),
            settled_green=False,
            settled_color_pair=self._pair_for_color(STYLES.get('boot_security_level', {}).get('settled_color', Settings.ui_colors.title)),
        )
        line_y += 2

        # Spinner animation
        self._spinner(line_y, x - 2, duration=Settings.animation.status_effect_duration)
        time.sleep(0.2)

        # Transition
        time.sleep(0.2)

    def _draw_borders(self):
        h, w = self.stdscr.getmaxyx()
        # Box-drawing characters from styles
        style_border = STYLES.get('border', {})
        horiz = style_border.get('box_chars', {}).get('horiz', '─')
        vert = style_border.get('box_chars', {}).get('vert', '│')
        tl = style_border.get('box_chars', {}).get('tl', '┌')
        tr = style_border.get('box_chars', {}).get('tr', '┐')
        bl = style_border.get('box_chars', {}).get('bl', '└')
        br = style_border.get('box_chars', {}).get('br', '┘')

        color = curses.color_pair(self._pair_for_color(style_border.get('color', Settings.ui_colors.border)))
        # Top
        try:
            self.stdscr.addstr(0, 0, tl + horiz * (w - 2) + tr, color)
            # Middle verticals
            for y in range(1, h - 1):
                if w >= 2:
                    self.stdscr.addstr(y, 0, vert, color)
                    self.stdscr.addstr(y, w - 1, vert, color)
            # Bottom
            self.stdscr.addstr(h - 1, 0, bl + horiz * (w - 2) + br, color)
        except Exception:
            pass

    def _draw_header(self):
        h, w = self.stdscr.getmaxyx()
        # Title centered
        total_len = len(PRTS_TITLE_PART1) + len(PRTS_TITLE_PART2)
        x = max(1, (w - total_len) // 2)
        y = 1
        if not self.did_scramble_title:
            # PRTS part
            style_prts = STYLES.get('title_prts', {})
            self._scramble(
                y,
                x,
                PRTS_TITLE_PART1,
                color_pair=self._pair_for_color(style_prts.get('color', Settings.ui_colors.text)),
                speed=style_prts.get('type_speed', Settings.animation.prts_speed),
                per_char_duration=style_prts.get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration),
                settled_green=style_prts.get('settled_green', False),
                settled_color_pair=self._pair_for_color(style_prts.get('settled_color', Settings.ui_colors.text)),
            )
            # Rest of title
            style_rest = STYLES.get('title_rest', {})
            self._scramble(
                y,
                x + len(PRTS_TITLE_PART1),
                PRTS_TITLE_PART2,
                color_pair=self._pair_for_color(style_rest.get('color', Settings.ui_colors.title)),
                speed=style_rest.get('type_speed', Settings.animation.type_writer_fast),
                per_char_duration=style_rest.get('per_char_scramble_duration', Settings.animation.per_char_scramble_duration),
                settled_green=style_rest.get('settled_green', False),
                settled_color_pair=self._pair_for_color(style_rest.get('settled_color', Settings.ui_colors.title)),
            )
            self.did_scramble_title = True
        else:
            try:
                # PRTS part
                style_prts = STYLES.get('title_prts', {})
                prts_attr = curses.color_pair(self._pair_for_color(style_prts.get('color', Settings.ui_colors.text)))
                if style_prts.get('bold', True):
                    prts_attr |= curses.A_BOLD
                self.stdscr.addstr(y, x, PRTS_TITLE_PART1, prts_attr)

                # Rest of title
                style_rest = STYLES.get('title_rest', {})
                rest_attr = curses.color_pair(self._pair_for_color(style_rest.get('color', Settings.ui_colors.title)))
                if style_rest.get('bold', True):
                    rest_attr |= curses.A_BOLD
                self.stdscr.addstr(y, x + len(PRTS_TITLE_PART1), PRTS_TITLE_PART2, rest_attr)
            except Exception:
                pass

        # Time at top right
        clock = time.strftime("%H:%M:%S")
        style_clock = STYLES.get('clock', {})
        clock_attr = curses.color_pair(self._pair_for_color(style_clock.get('color', Settings.ui_colors.text)))
        if style_clock.get('bold', True):
            clock_attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(1, max(2, w - len(clock) - 2), clock, clock_attr)
        except Exception:
            pass

    def _draw_footer(self):
        h, w = self.stdscr.getmaxyx()
        txt = FOOTER
        x = max(1, (w - len(txt)) // 2)
        style_footer = STYLES.get('footer', {})
        footer_attr = curses.color_pair(self._pair_for_color(style_footer.get('color', Settings.ui_colors.border)))
        try:
            self.stdscr.addstr(h - 2, x, txt, footer_attr)
        except Exception:
            pass

    def _draw_status_panel(self):
        h, w = self.stdscr.getmaxyx()
        panel_w = max(40, min(60, w // 2))
        panel_h = 6
        y0 = 3
        x0 = 2

        # Panel border
        style_border = STYLES.get('status_panel_border', {})
        panel_border_attr = curses.color_pair(self._pair_for_color(style_border.get('color', Settings.ui_colors.border)))
        try:
            self.stdscr.addstr(y0, x0, '┌' + '─' * (panel_w - 2) + '┐', panel_border_attr)
            for y in range(1, panel_h - 1):
                self.stdscr.addstr(y0 + y, x0, '│' + ' ' * (panel_w - 2) + '│', panel_border_attr)
            self.stdscr.addstr(y0 + panel_h - 1, x0, '└' + '─' * (panel_w - 2) + '┘', panel_border_attr)
        except Exception:
            pass

        # Panel title (scramble once)
        title = "STATUS: WINDOW"
        style_title = STYLES.get('status_panel_title', {})
        title_attr = curses.color_pair(self._pair_for_color(style_title.get('color', Settings.ui_colors.title)))
        if style_title.get('bold', True):
            title_attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(y0, x0 + 2, title, title_attr)
        except Exception:
            pass

        # Window info
        style_text = STYLES.get('text_default', {})
        text_attr = curses.color_pair(self._pair_for_color(style_text.get('color', Settings.ui_colors.text)))
        style_warning = STYLES.get('status_warning', {})
        warning_attr = curses.color_pair(self._pair_for_color(style_warning.get('color', Settings.ui_colors.warning)))
        if style_warning.get('bold', True):
            warning_attr |= curses.A_BOLD
        try:
            ark_window.refresh_window_info()
            if getattr(ark_window, 'window', None):
                left = ark_window.window['left']
                top = ark_window.window['top']
                width = ark_window.width
                height = ark_window.height
                self.stdscr.addstr(y0 + 2, x0 + 2, f"Position: ({left},{top})", text_attr)
                self.stdscr.addstr(y0 + 3, x0 + 2, f"Resolution: {width} x {height}", text_attr)
            else:
                self.stdscr.addstr(y0 + 2, x0 + 2, "Warning: Window Not Found", warning_attr)
                self.stdscr.addstr(y0 + 3, x0 + 2, "Position: (n/a)   Resolution: n/a", text_attr)
        except Exception:
            try:
                self.stdscr.addstr(y0 + 2, x0 + 2, "Warning: Window Not Found", warning_attr)
                self.stdscr.addstr(y0 + 3, x0 + 2, "Position: (n/a)   Resolution: n/a", text_attr)
            except Exception:
                pass

    # --- Toast messages ---
    def post_message(self, text: str, level: str = 'info'):
        priority = {'info': 1, 'warning': 2, 'error': 3}
        now = time.time()
        duration = max(4.0, Settings.animation.status_effect_duration)
        if getattr(self, '_toast', None) and self._toast.get('expires', 0) > now:
            if priority.get(level, 1) <= priority.get(self._toast.get('level', 'info'), 1):
                return
        self._toast = {'text': text, 'level': level, 'expires': now + duration}

    def _draw_toast(self):
        if not getattr(self, '_toast', None):
            return
        now = time.time()
        if self._toast.get('expires', 0) <= now:
            self._toast = None
            return
        level = self._toast.get('level', 'info')
        style_toast = STYLES.get(f'toast_{level}', STYLES.get('toast_info', {}))
        toast_attr = curses.color_pair(self._pair_for_color(style_toast.get('color', Settings.ui_colors.text)))
        if style_toast.get('bold', level in ('warning', 'error')):
            toast_attr |= curses.A_BOLD
        text = self._toast.get('text', '')
        h, w = self.stdscr.getmaxyx()
        x = max(2, (w - len(text)) // 2)
        y = max(1, h - 4)
        try:
            self.stdscr.addstr(y, x, text, toast_attr)
        except Exception:
            pass

    def _draw_menu(self):
        h, w = self.stdscr.getmaxyx()
        start_y = 10
        x = 4
        style_menu_header = STYLES.get('settings_header', {})  # Reuse settings header style
        header_attr = curses.color_pair(self._pair_for_color(style_menu_header.get('color', Settings.ui_colors.title)))
        if style_menu_header.get('bold', True):
            header_attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(start_y - 2, x, "OPERATIONS", header_attr)
        except Exception:
            pass
        for i, (label, key) in enumerate(self.menu_items, start=1):
            y = start_y + i - 1
            idx = i - 1
            number_prefix = f"{i}. "
            line = number_prefix + label
            if idx == self.selected_index and self.view == 'menu':
                style_selected = STYLES.get('menu_item_selected', {})
                selected_attr = curses.color_pair(self._pair_for_color(style_selected.get('color', Settings.ui_colors.selection_fg)))
                if style_selected.get('bold', True):
                    selected_attr |= curses.A_BOLD
                try:
                    self.stdscr.addstr(y, x, line.ljust(w - x - 2), selected_attr)
                except Exception:
                    pass
            else:
                style_item = STYLES.get('menu_item', {})
                item_attr = curses.color_pair(self._pair_for_color(style_item.get('color', Settings.ui_colors.text)))
                try:
                    self.stdscr.addstr(y, x, line, item_attr)
                except Exception:
                    pass

    def _settings_get_value(self, path: str):
        if path == 'safety.dry_run':
            return bool(Settings.safety.dry_run)
        if path == 'observability.enable_failure_screenshots':
            return bool(Settings.observability.enable_failure_screenshots)
        if path == 'safety.enable_panic_key':
            return bool(Settings.safety.enable_panic_key)
        if path == 'logging.console_level':
            return get_console_level()
        if path == 'logging.enabled':
            return bool(Settings.logging.enabled)
        if path == 'arknights.use_expedite':
            return bool(Settings.arknights.use_expedite)
        if path == 'arknights.finish_on_recruitment':
            return bool(Settings.arknights.finish_on_recruitment)
        if path == 'arknights.use_total_proxy':
            return bool(Settings.arknights.use_total_proxy)
        if path == 'arknights.store_based_on':
            return list(Settings.arknights.store_based_on)
        if path == 'arknights.store_rarity_priority':
            return list(Settings.arknights.store_rarity_priority)
        return False

    def _settings_toggle(self, path: str):
        if path == 'safety.dry_run':
            cur = Settings.safety
            Settings.safety = replace(cur, dry_run=not cur.dry_run)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'observability.enable_failure_screenshots':
            cur = Settings.observability
            Settings.observability = replace(cur, enable_failure_screenshots=not cur.enable_failure_screenshots)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'safety.enable_panic_key':
            cur = Settings.safety
            Settings.safety = replace(cur, enable_panic_key=not cur.enable_panic_key)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'logging.console_level':
            # Cycle levels: DEBUG -> INFO -> WARNING -> ERROR -> DEBUG
            order = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
            cur = get_console_level()
            try:
                idx = (order.index(cur) + 1) % len(order)
            except ValueError:
                idx = 1
            set_console_level(order[idx])
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'logging.enabled':
            cur = Settings.logging
            new_enabled = not cur.enabled
            set_logging_enabled(new_enabled)
            Settings.logging = replace(cur, enabled=new_enabled)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'arknights.use_expedite':
            cur = Settings.arknights
            Settings.arknights = replace(cur, use_expedite=not cur.use_expedite)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'arknights.finish_on_recruitment':
            cur = Settings.arknights
            Settings.arknights = replace(cur, finish_on_recruitment=not cur.finish_on_recruitment)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        if path == 'arknights.use_total_proxy':
            cur = Settings.arknights
            Settings.arknights = replace(cur, use_total_proxy=not cur.use_total_proxy)
            try:
                save_user_settings()
            except Exception:
                pass
            return
        # list settings handled in _handle_automation_key via rotation

    def _draw_settings(self):
        h, w = self.stdscr.getmaxyx()
        start_y = 10
        x = 4
        header = "PRTS SYSTEM SETTINGS"
        style_header = STYLES.get('settings_header', {})
        header_attr = curses.color_pair(self._pair_for_color(style_header.get('color', Settings.ui_colors.title)))
        if style_header.get('bold', True):
            header_attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(start_y - 2, x, header, header_attr)
        except Exception:
            pass

        for i, (label, path) in enumerate(self.settings_items, start=1):
            y = start_y + i - 1
            val = self._settings_get_value(path)
            if isinstance(val, bool):
                state_text = "ON" if val else "OFF"
                style_state = STYLES.get('settings_value_on' if val else 'settings_value_off', {})
                state_color = curses.color_pair(self._pair_for_color(style_state.get('color', Settings.ui_colors.on if val else Settings.ui_colors.off)))
                if style_state.get('bold', True):
                    state_color |= curses.A_BOLD
            else:
                state_text = str(val)
                style_state = STYLES.get('text_default', {})
                state_color = curses.color_pair(self._pair_for_color(style_state.get('color', Settings.ui_colors.text)))
            line = f"{i}. {label}: {state_text}"
            if (i - 1) == self.settings_index and self.view == 'settings':
                style_selected = STYLES.get('menu_item_selected', {})
                selected_attr = curses.color_pair(self._pair_for_color(style_selected.get('color', Settings.ui_colors.selection_fg)))
                if style_selected.get('bold', True):
                    selected_attr |= curses.A_BOLD
                try:
                    self.stdscr.addstr(y, x, line.ljust(w - x - 2), selected_attr)
                except Exception:
                    pass
            else:
                try:
                    # label
                    style_label = STYLES.get('settings_label', {})
                    label_attr = curses.color_pair(self._pair_for_color(style_label.get('color', Settings.ui_colors.text)))
                    self.stdscr.addstr(y, x, f"{i}. {label}: ", label_attr)
                    # state
                    self.stdscr.addstr(y, x + len(f"{i}. {label}: "), state_text, state_color)
                except Exception:
                    pass

        hint = "Use ↑/↓ to navigate, Enter/Space to toggle, B to go back"
        style_hint = STYLES.get('settings_hint', {})
        hint_attr = curses.color_pair(self._pair_for_color(style_hint.get('color', Settings.ui_colors.border)))
        try:
            x_hint = max(2, (w - len(hint)) // 2)
            self.stdscr.addstr(h - 3, x_hint, hint, hint_attr)
        except Exception:
            pass

    def _draw_automation_settings(self):
        h, w = self.stdscr.getmaxyx()
        start_y = 10
        x = 4
        header = "AUTOMATION SETTINGS"
        style_header = STYLES.get('auto_section_header', {})
        header_attr = curses.color_pair(self._pair_for_color(style_header.get('color', Settings.ui_colors.title)))
        if style_header.get('bold', True):
            header_attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(start_y - 2, x, header, header_attr)
        except Exception:
            pass

        display_idx = 0
        y = start_y
        item_counter = 1
        for section_title, items in self.automation_sections:
            # Section header
            style_section = STYLES.get('auto_section_header', {})
            section_attr = curses.color_pair(self._pair_for_color(style_section.get('color', Settings.ui_colors.title)))
            if style_section.get('bold', True):
                section_attr |= curses.A_BOLD
            try:
                self.stdscr.addstr(y, x, f"[{section_title}]", section_attr)
            except Exception:
                pass
            y += 1
            for (label, path) in items:
                val = self._settings_get_value(path)
                if isinstance(val, bool):
                    state_text = "ON" if val else "OFF"
                    style_state = STYLES.get('auto_value_on' if val else 'auto_value_off', {})
                    state_color = curses.color_pair(self._pair_for_color(style_state.get('color', Settings.ui_colors.on if val else Settings.ui_colors.off)))
                    if style_state.get('bold', True):
                        state_color |= curses.A_BOLD
                elif isinstance(val, list):
                    if path == 'arknights.store_based_on':
                        state_text = ' > '.join(val)
                    else:
                        state_text = ', '.join(val)
                    style_state = STYLES.get('auto_value_list', {})
                    state_color = curses.color_pair(self._pair_for_color(style_state.get('color', Settings.ui_colors.text)))
                else:
                    state_text = str(val)
                    style_state = STYLES.get('text_default', {})
                    state_color = curses.color_pair(self._pair_for_color(style_state.get('color', Settings.ui_colors.text)))

                prefix = f"{item_counter}. {label}: "
                highlight = (display_idx == self.automation_index and self.view == 'automation')
                y = self._draw_wrapped_line(y, x, prefix, state_text, w, highlight, state_color)
                display_idx += 1
                item_counter += 1
        hint = "Use ↑/↓ to navigate, Enter/Space to toggle, ◄/► rotate lists, R reset, B back"
        style_hint = STYLES.get('auto_hint', {})
        hint_attr = curses.color_pair(self._pair_for_color(style_hint.get('color', Settings.ui_colors.border)))
        try:
            x_hint = max(2, (w - len(hint)) // 2)
            self.stdscr.addstr(h - 3, x_hint, hint, hint_attr)
        except Exception:
            pass

    def _draw_wrapped_line(self, y: int, x: int, prefix: str, value: str, total_w: int, highlight: bool, value_color) -> int:
        maxw = total_w - x - 2
        words = value.split(' ')
        lines: List[str] = []
        current = ''
        for w in words:
            piece = ('' if current == '' else ' ') + w
            base_len = len(prefix) if not lines else 3
            if base_len + len(current) + len(piece) <= maxw:
                current += piece
            else:
                lines.append(current)
                current = w
        if current:
            lines.append(current)
        for idx, line in enumerate(lines):
            line_prefix = prefix if idx == 0 else '   '
            if highlight:
                style_selected = STYLES.get('menu_item_selected', {})
                selected_attr = curses.color_pair(self._pair_for_color(style_selected.get('color', Settings.ui_colors.selection_fg)))
                if style_selected.get('bold', True):
                    selected_attr |= curses.A_BOLD
                try:
                    self.stdscr.addstr(y, x, (line_prefix + line).ljust(maxw), selected_attr)
                except Exception:
                    pass
            else:
                try:
                    style_label = STYLES.get('auto_label', {})
                    label_attr = curses.color_pair(self._pair_for_color(style_label.get('color', Settings.ui_colors.text)))
                    self.stdscr.addstr(y, x, line_prefix, label_attr)
                    self.stdscr.addstr(y, x + len(line_prefix), line, value_color | curses.A_BOLD)
                except Exception:
                    pass
            y += 1
        return y

    # --- Event handling ---
    def _handle_menu_key(self, ch: int) -> bool:
        if ch in (curses.KEY_UP, ord('k')):
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            return True
        if ch in (curses.KEY_DOWN, ord('j')):
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            return True
        # number keys
        if ord('1') <= ch <= ord(str(len(self.menu_items))):
            self.selected_index = ch - ord('1')
            return True
        # Enter
        if ch in (curses.KEY_ENTER, 10, 13):
            return self._activate_menu()
        # direct keys
        if ch in (ord('s'), ord('S')):
            self.view = 'settings'
            self.settings_index = 0
            return True
        if ch in (ord('q'), ord('Q')):
            raise KeyboardInterrupt
        return False

    def _activate_menu(self) -> bool:
        label, key = self.menu_items[self.selected_index]
        logger.info(f"[interface] Selected menu item: {label}")
        if key == 'quit':
            raise KeyboardInterrupt
        if key == 'settings':
            self.view = 'settings'
            self.settings_index = 0
            return True
        if key == 'automation':
            self.view = 'automation'
            self.automation_index = 0
            return True
        if key == 'return_menu':
            try:
                MainMenu().return_to_main_menu()
            except Exception:
                pass
            return True
        # Execute selected automation using fresh aggregator to capture current Settings
        agg = TaskAggregator()
        try:
            if key == 'run_all':
                agg.run_all_dailies()
            elif key == 'recruit':
                agg.run_recruitment_dailies()
            elif key == 'base':
                agg.run_base_dailies()
            elif key == 'friends':
                agg.run_friends_dailies()
            elif key == 'store':
                agg.run_store_tasks()
            elif key == 'missions':
                agg.run_missions_dailies()
            elif key == 'terminal':
                agg.run_terminal_dailies()
        except Exception:
            pass
        # Post completion message
        self.post_message(f"Executed: {label}", level='info')
        return True

    def _handle_settings_key(self, ch: int) -> bool:
        if ch in (curses.KEY_UP, ord('k')):
            self.settings_index = (self.settings_index - 1) % len(self.settings_items)
            return True
        if ch in (curses.KEY_DOWN, ord('j')):
            self.settings_index = (self.settings_index + 1) % len(self.settings_items)
            return True
        if ch in (curses.KEY_ENTER, 10, 13, ord(' ')):
            _, path = self.settings_items[self.settings_index]
            self._settings_toggle(path)
            return True
        if ch in (ord('b'), ord('B')):
            self.view = 'menu'
            return True
        if ch in (ord('q'), ord('Q')):
            raise KeyboardInterrupt
        return False

    def _handle_automation_key(self, ch: int) -> bool:
        flat = self._automation_flat_items()
        if ch in (curses.KEY_UP, ord('k')):
            self.automation_index = (self.automation_index - 1) % len(flat)
            return True
        if ch in (curses.KEY_DOWN, ord('j')):
            self.automation_index = (self.automation_index + 1) % len(flat)
            return True
        label, path = flat[self.automation_index]
        # List rotation for store settings
        if path in ('arknights.store_based_on', 'arknights.store_rarity_priority'):
            if ch in (curses.KEY_LEFT, ord('h')):
                cur = Settings.arknights
                lst = list(getattr(cur, path.split('.')[-1]))
                if lst:
                    lst = lst[1:] + lst[:1]
                    Settings.arknights = replace(cur, **{path.split('.')[-1]: lst})
                    try:
                        save_user_settings()
                    except Exception:
                        pass
                return True
            if ch in (curses.KEY_RIGHT, ord('l')):
                cur = Settings.arknights
                lst = list(getattr(cur, path.split('.')[-1]))
                if lst:
                    lst = lst[-1:] + lst[:-1]
                    Settings.arknights = replace(cur, **{path.split('.')[-1]: lst})
                    try:
                        save_user_settings()
                    except Exception:
                        pass
                return True
            if ch in (ord('r'), ord('R')):
                # reset to defaults from dataclass
                cur = Settings.arknights
                from dataclasses import fields
                defaults = {f.name: getattr(type(cur)(), f.name) for f in fields(cur)}
                Settings.arknights = replace(cur, **{
                    path.split('.')[-1]: list(defaults[path.split('.')[-1]])
                })
                try:
                    save_user_settings()
                except Exception:
                    pass
                return True
        if ch in (curses.KEY_ENTER, 10, 13, ord(' ')):
            self._settings_toggle(path)
            return True
        if ch in (ord('b'), ord('B')):
            self.view = 'menu'
            return True
        if ch in (ord('q'), ord('Q')):
            raise KeyboardInterrupt
        return False

    # --- Main loop ---
    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        self._init_colors()
        # Load settings on startup
        load_user_settings()

        last_clock = 0.0
        # Boot sequence first
        self.stdscr.nodelay(False)
        self._boot_sequence()
        self.stdscr.nodelay(True)
        while True:
            self.stdscr.erase()
            self._draw_borders()
            self._draw_header()
            self._draw_status_panel()
            if self.view == 'menu':
                self._draw_menu()
            elif self.view == 'settings':
                self._draw_settings()
            else:
                self._draw_automation_settings()
            self._draw_footer()
            self._draw_toast()

            self.stdscr.refresh()

            # Input with small timeout to allow clock to update
            try:
                ch = self.stdscr.getch()
            except Exception:
                ch = -1
            if ch != -1:
                try:
                    if self.view == 'menu':
                        self._handle_menu_key(ch)
                    elif self.view == 'settings':
                        self._handle_settings_key(ch)
                    else:
                        self._handle_automation_key(ch)
                except KeyboardInterrupt:
                    # Save settings before exit
                    try:
                        save_user_settings()
                    except Exception:
                        pass
                    break
            else:
                # throttle loop a bit
                time.sleep(0.05)


def run_console():
    def _wrapped(stdscr):
        ui = PRTSInterface(stdscr)
        ui.run()
    curses.wrapper(_wrapped)


if __name__ == "__main__":
    run_console()


