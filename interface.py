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


locale.setlocale(locale.LC_ALL, '')


TITLE = "PRTS Task Automation Project"
FOOTER = "// Connection to Rhodes Island PRTS system established //"


class PRTSInterface:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.selected_index = 0
        self.view = 'menu'  # 'menu' | 'settings' | 'automation'
        self.settings_index = 0
        self.did_scramble_title = False
        self.automation_index = 0

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

        # Automation settings page
        self.automation_items: List[Tuple[str, str]] = [
            ("Use Expedite (Recruitment)", "arknights.use_expedite"),
            ("Finish On Recruitment", "arknights.finish_on_recruitment"),
            ("Use Total Proxy", "arknights.use_total_proxy"),
            ("Purchase Order", "arknights.store_based_on"),
            ("Rarity Priority", "arknights.store_rarity_priority"),
        ]

    # --- Draw helpers ---
    def _init_colors(self):
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        # Pairs
        curses.init_pair(1, curses.COLOR_CYAN, -1)    # borders
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # title
        curses.init_pair(3, curses.COLOR_GREEN, -1)   # ON
        curses.init_pair(4, curses.COLOR_RED, -1)     # OFF
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)  # selection (high contrast)
        curses.init_pair(6, curses.COLOR_WHITE, -1)   # normal text (white)

    def _scramble(self, y: int, x: int, text: str, color_pair: int = 2, duration: float = None, per_char: bool = True, settled_green: bool = False, speed: float = None, per_char_duration: float = None):
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
                    self.stdscr.addstr(y, cx, ch, curses.color_pair(3) | curses.A_BOLD)
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

    def _dots(self, y: int, x: int, count: int = 3, color_pair: int = 6):
        delay = max(0.001, Settings.animation.dots_delay)
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
        frames = ['⠋','⠙','⠸','⠴','⠦','⠇']
        t0 = time.time()
        i = 0
        while time.time() - t0 < duration:
            try:
                self.stdscr.addstr(y, x, frames[i % len(frames)], curses.color_pair(2))
                self.stdscr.refresh()
            except Exception:
                pass
            time.sleep(0.1)
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
        # Welcome (fast)
        self._scramble(
            y,
            x,
            welcome,
            color_pair=2,
            speed=Settings.animation.welcome_speed,
            per_char_duration=Settings.animation.per_char_scramble_duration / 2,
            settled_green=False,
        )
        # Username (slower per-char flicker, then green)
        self._scramble(
            y,
            x + len(welcome),
            name,
            color_pair=2,
            speed=Settings.animation.username_speed,
            per_char_duration=max(Settings.animation.per_char_scramble_duration, 0.15),
            settled_green=True,
        )

        # Boot messages
        line_y = y + 3
        # 1) Administrator Privileges ... ON
        msg = "Administrator Privileges"
        self._typewriter(line_y, x, msg, color_pair=6, bold=True)
        self._typewriter(line_y, x + len(msg) + 1, " ", color_pair=6)
        self._dots(line_y, x + len(msg) + 1)
        on_text = "ON"
        self._scramble(
            line_y,
            x + len(msg) + 1,
            on_text,
            color_pair=2,
            per_char_duration=Settings.animation.per_char_scramble_duration,
            settled_green=True,
        )
        line_y += 2

        # 2) Rhodes Island Terminal Link: STABLE
        msg2 = "Rhodes Island Terminal Link: "
        self._typewriter(line_y, x, msg2, color_pair=6)
        self._scramble(
            line_y,
            x + len(msg2),
            "STABLE",
            color_pair=2,
            per_char_duration=Settings.animation.per_char_scramble_duration,
            settled_green=True,
        )
        line_y += 2

        # 3) Security Clearance Level: 3
        msg3 = "Security Clearance Level: "
        self._typewriter(line_y, x, msg3, color_pair=6)
        self._scramble(
            line_y,
            x + len(msg3),
            "3",
            color_pair=2,
            per_char_duration=Settings.animation.per_char_scramble_duration,
            settled_green=False,
        )
        line_y += 2

        # Spinner animation
        self._spinner(line_y, x - 2, duration=Settings.animation.status_effect_duration)
        time.sleep(0.2)

        # Transition
        time.sleep(0.2)

    def _draw_borders(self):
        h, w = self.stdscr.getmaxyx()
        # Box-drawing characters
        horiz = '─'
        vert = '│'
        tl = '┌'
        tr = '┐'
        bl = '└'
        br = '┘'

        color = curses.color_pair(1)
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
        x = max(1, (w - len(TITLE)) // 2)
        y = 1
        if not self.did_scramble_title:
            self._scramble(y, x, TITLE, color_pair=2, duration=0.6)
            self.did_scramble_title = True
        else:
            try:
                self.stdscr.addstr(y, x, TITLE, curses.color_pair(2) | curses.A_BOLD)
            except Exception:
                pass

        # Time at top right
        clock = time.strftime("%H:%M:%S")
        try:
            self.stdscr.addstr(1, max(2, w - len(clock) - 2), clock, curses.color_pair(6) | curses.A_BOLD)
        except Exception:
            pass

    def _draw_footer(self):
        h, w = self.stdscr.getmaxyx()
        txt = FOOTER
        x = max(1, (w - len(txt)) // 2)
        try:
            self.stdscr.addstr(h - 2, x, txt, curses.color_pair(1))
        except Exception:
            pass

    def _draw_status_panel(self):
        h, w = self.stdscr.getmaxyx()
        panel_w = max(40, min(60, w // 2))
        panel_h = 6
        y0 = 3
        x0 = 2

        # Panel border
        try:
            self.stdscr.addstr(y0, x0, '┌' + '─' * (panel_w - 2) + '┐', curses.color_pair(1))
            for y in range(1, panel_h - 1):
                self.stdscr.addstr(y0 + y, x0, '│' + ' ' * (panel_w - 2) + '│', curses.color_pair(1))
            self.stdscr.addstr(y0 + panel_h - 1, x0, '└' + '─' * (panel_w - 2) + '┘', curses.color_pair(1))
        except Exception:
            pass

        # Panel title (scramble once)
        title = "STATUS: WINDOW"
        try:
            self.stdscr.addstr(y0, x0 + 2, title, curses.color_pair(2) | curses.A_BOLD)
        except Exception:
            pass

        # Window info
        try:
            ark_window.refresh_window_info()
            left = ark_window.window['left']
            top = ark_window.window['top']
            width = ark_window.width
            height = ark_window.height
            self.stdscr.addstr(y0 + 2, x0 + 2, f"Position: ({left},{top})", curses.color_pair(6))
            self.stdscr.addstr(y0 + 3, x0 + 2, f"Resolution: {width} x {height}", curses.color_pair(6))
        except Exception as ex:
            logger.debug(f"[interface] Failed to read window info: {ex}")
            try:
                self.stdscr.addstr(y0 + 2, x0 + 2, "Position: (n/a)", curses.color_pair(6))
                self.stdscr.addstr(y0 + 3, x0 + 2, "Resolution: n/a", curses.color_pair(6))
            except Exception:
                pass

    def _draw_menu(self):
        h, w = self.stdscr.getmaxyx()
        start_y = 10
        x = 4
        try:
            self.stdscr.addstr(start_y - 2, x, "OPERATIONS", curses.color_pair(2) | curses.A_BOLD)
        except Exception:
            pass
        for i, (label, key) in enumerate(self.menu_items, start=1):
            y = start_y + i - 1
            idx = i - 1
            number_prefix = f"{i}. "
            line = number_prefix + label
            if idx == self.selected_index and self.view == 'menu':
                try:
                    self.stdscr.addstr(y, x, line.ljust(w - x - 2), curses.color_pair(5) | curses.A_BOLD)
                except Exception:
                    pass
            else:
                try:
                    self.stdscr.addstr(y, x, line, curses.color_pair(6))
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
            return
        if path == 'observability.enable_failure_screenshots':
            cur = Settings.observability
            Settings.observability = replace(cur, enable_failure_screenshots=not cur.enable_failure_screenshots)
            return
        if path == 'safety.enable_panic_key':
            cur = Settings.safety
            Settings.safety = replace(cur, enable_panic_key=not cur.enable_panic_key)
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
            return
        if path == 'logging.enabled':
            cur = Settings.logging
            new_enabled = not cur.enabled
            set_logging_enabled(new_enabled)
            Settings.logging = replace(cur, enabled=new_enabled)
            return
        if path == 'arknights.use_expedite':
            cur = Settings.arknights
            Settings.arknights = replace(cur, use_expedite=not cur.use_expedite)
            return
        if path == 'arknights.finish_on_recruitment':
            cur = Settings.arknights
            Settings.arknights = replace(cur, finish_on_recruitment=not cur.finish_on_recruitment)
            return
        if path == 'arknights.use_total_proxy':
            cur = Settings.arknights
            Settings.arknights = replace(cur, use_total_proxy=not cur.use_total_proxy)
            return
        # list settings handled in _handle_automation_key via rotation

    def _draw_settings(self):
        h, w = self.stdscr.getmaxyx()
        start_y = 10
        x = 4
        header = "PRTS SYSTEM SETTINGS"
        try:
            self.stdscr.addstr(start_y - 2, x, header, curses.color_pair(2) | curses.A_BOLD)
        except Exception:
            pass

        for i, (label, path) in enumerate(self.settings_items, start=1):
            y = start_y + i - 1
            val = self._settings_get_value(path)
            if isinstance(val, bool):
                state_text = "ON" if val else "OFF"
                state_color = curses.color_pair(3) if val else curses.color_pair(4)
            else:
                state_text = str(val)
                state_color = curses.color_pair(6)
            line = f"{i}. {label}: {state_text}"
            if (i - 1) == self.settings_index and self.view == 'settings':
                try:
                    self.stdscr.addstr(y, x, line.ljust(w - x - 2), curses.color_pair(5) | curses.A_BOLD)
                except Exception:
                    pass
            else:
                try:
                    # label
                    self.stdscr.addstr(y, x, f"{i}. {label}: ", curses.color_pair(6))
                    # state
                    self.stdscr.addstr(y, x + len(f"{i}. {label}: "), state_text, state_color | curses.A_BOLD)
                except Exception:
                    pass

        hint = "Use ↑/↓ to navigate, Enter/Space to toggle, B to go back"
        try:
            self.stdscr.addstr(h - 3, 2, hint, curses.color_pair(1))
        except Exception:
            pass

    def _draw_automation_settings(self):
        h, w = self.stdscr.getmaxyx()
        start_y = 10
        x = 4
        header = "AUTOMATION SETTINGS"
        try:
            self.stdscr.addstr(start_y - 2, x, header, curses.color_pair(2) | curses.A_BOLD)
        except Exception:
            pass

        for i, (label, path) in enumerate(self.automation_items, start=1):
            y = start_y + i - 1
            val = self._settings_get_value(path)
            if isinstance(val, bool):
                state_text = "ON" if val else "OFF"
                state_color = curses.color_pair(3) if val else curses.color_pair(4)
            elif isinstance(val, list):
                if path == 'arknights.store_based_on':
                    state_text = ' > '.join(val)
                else:
                    state_text = ', '.join(val)
                state_color = curses.color_pair(6)
            else:
                state_text = str(val)
                state_color = curses.color_pair(6)
            line = f"{i}. {label}: {state_text}"
            if (i - 1) == self.automation_index and self.view == 'automation':
                try:
                    self.stdscr.addstr(y, x, line.ljust(w - x - 2), curses.color_pair(5) | curses.A_BOLD)
                except Exception:
                    pass
            else:
                try:
                    self.stdscr.addstr(y, x, f"{i}. {label}: ", curses.color_pair(6))
                    self.stdscr.addstr(y, x + len(f"{i}. {label}: "), state_text, state_color | curses.A_BOLD)
                except Exception:
                    pass
        hint = "Use ↑/↓ to navigate, Enter/Space to toggle, ◄/► rotate lists, R reset, B back"
        try:
            self.stdscr.addstr(h - 3, 2, hint, curses.color_pair(1))
        except Exception:
            pass

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
        # For now, just flash a notice; execution hooks can be added later
        h, w = self.stdscr.getmaxyx()
        msg = f"Executed: {label}"
        try:
            self.stdscr.addstr(h - 4, max(2, (w - len(msg)) // 2), msg, curses.color_pair(2) | curses.A_BOLD)
            self.stdscr.refresh()
        except Exception:
            pass
        time.sleep(0.6)
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
        if ch in (curses.KEY_UP, ord('k')):
            self.automation_index = (self.automation_index - 1) % len(self.automation_items)
            return True
        if ch in (curses.KEY_DOWN, ord('j')):
            self.automation_index = (self.automation_index + 1) % len(self.automation_items)
            return True
        label, path = self.automation_items[self.automation_index]
        # List rotation for store settings
        if path in ('arknights.store_based_on', 'arknights.store_rarity_priority'):
            if ch in (curses.KEY_LEFT, ord('h')):
                cur = Settings.arknights
                lst = list(getattr(cur, path.split('.')[-1]))
                if lst:
                    lst = lst[1:] + lst[:1]
                    Settings.arknights = replace(cur, **{path.split('.')[-1]: lst})
                return True
            if ch in (curses.KEY_RIGHT, ord('l')):
                cur = Settings.arknights
                lst = list(getattr(cur, path.split('.')[-1]))
                if lst:
                    lst = lst[-1:] + lst[:-1]
                    Settings.arknights = replace(cur, **{path.split('.')[-1]: lst})
                return True
            if ch in (ord('r'), ord('R')):
                # reset to defaults from dataclass
                cur = Settings.arknights
                from dataclasses import fields
                defaults = {f.name: getattr(type(cur)(), f.name) for f in fields(cur)}
                Settings.arknights = replace(cur, **{
                    path.split('.')[-1]: list(defaults[path.split('.')[-1]])
                })
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


