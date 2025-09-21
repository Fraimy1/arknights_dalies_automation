from os import name
import os
import random
from typing import List, Optional, Tuple, Union
import re
import time

from PIL.ImageChops import screen
from time import sleep
import pyautogui as pg
import pygetwindow as gw
import mss
import numpy as np
import math
from logger import logger
from config import Settings
from waits import Wait
from elements import get_element, UIElement
import states as _states
from PIL import Image, ImageDraw

pg.FAILSAFE = False # Nothing can possibly go wrong with this, right?

def get_arknights_window_title(keywords_to_exclude=None):
    """Get the title of the Arknights window, being more specific."""
    if keywords_to_exclude is None:
        keywords_to_exclude = []
    
    # Add default keywords to a new list to avoid modifying the default
    all_keywords_to_exclude = keywords_to_exclude + ['arknights_dalies_automation', 'dailies', 'visual studio code', '.py']

    windows = gw.getAllWindows()
    
    # First, look for a perfect match
    for w in windows:
        if w.title.lower().strip() == "arknights":
            logger.debug(f"Found perfect match for Arknights window: {w.title}")
            return w.title

    # If no perfect match, search for a window that contains "arknights" but not excluded keywords
    potential_windows = []
    for w in windows:
        title_lower = w.title.lower().strip()
        if "arknights" in title_lower and not any(ex_word in title_lower for ex_word in all_keywords_to_exclude):
            potential_windows.append(w)

    if potential_windows:
        logger.debug(f"Found potential Arknights window: {potential_windows[0].title}")
        return potential_windows[0].title
        
    logger.warning("Could not find the Arknights window.")
    return None

def get_window_info(window_title):
    """Get the position and size of a window by its title, preferring an exact match."""
    if not window_title:
        logger.warning("get_window_info called with an empty title.")
        return None

    windows = gw.getWindowsWithTitle(window_title)

    # Prefer an exact match to avoid ambiguity
    for window in windows:
        if window.title == window_title:
            info = {
                'left': window.left,
                'right': window.right,
                'top': window.top,
                'bottom': window.bottom,
                'width': window.width,
                'height': window.height,
                'title': window.title
            }
            return info
    
    logger.warning(f"No exact match for '{window_title}' found. Aborting to prevent errors.")
    return None

windowed_offsets = {
    'google_play': (9, 8, 31, 8)
}
#TODO: Implement a funciton that would put funciton to sleep until color disappears
#TODO: Implement a wrapper to update window before every function call

class ArknightsWindow:
    """Class to manage the Arknights window."""
    
    def __init__(self, title=None, windowed_mode_interface='google_play'):
        if title is None:
            title = get_arknights_window_title()
        self.title = title
        self.window = get_window_info(title)
        # Provide safe defaults if window is not available
        if self.window:
            self.width = self.window['width']
            self.height = self.window['height']
        else:
            self.width = 1920
            self.height = 1080
        self.last_screenshot = None
        self._last_frame_time = 0.0
        self._frame_max_age_ms = 50.0  # simple frame cache
        self.is_windowed = False

        # Safety/UX
        self._abort_flag = False
        self._dry_run = Settings.safety.dry_run

        self.windowed_mode_interface = windowed_mode_interface
        self.windowed_offset_left = windowed_offsets.get(windowed_mode_interface, 0)[0]
        self.windowed_offset_right = windowed_offsets.get(windowed_mode_interface, 0)[1]
        self.windowed_offset_top = windowed_offsets.get(windowed_mode_interface, 0)[2]
        self.windowed_offset_bottom = windowed_offsets.get(windowed_mode_interface, 0)[3]
        
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            self.offset_x = monitor['left']
            self.offset_y = monitor['top']
        logger.debug(f"ArknightsWindow initialized: title={self.title}, size=({self.width}x{self.height}), offsets=({self.offset_x},{self.offset_y})")

    def refresh_window_info(self):
        """Refresh window information in case window moved/resized."""
        old_size = (self.width, self.height)
        self.window = get_window_info(self.title)
        if self.window:
            self.width = self.window['width']
            self.height = self.window['height']
            if (self.width, self.height) != old_size:
                logger.debug(f"Window size changed from {old_size} to ({self.width},{self.height})")

    def get_scaled_coords(self, base_x, base_y,
                          base_w=1920, base_h=1080):
        """Return _window-relative_ coords, scaled to current size."""
        if self.is_windowed:
            # Adjust for windowed mode offsets
            base_x += self.windowed_offset_left
            base_y += self.windowed_offset_top
            base_w -= (self.windowed_offset_left + self.windowed_offset_right)
            base_h -= (self.windowed_offset_top + self.windowed_offset_bottom)

        scale_x = int(base_x * self.width / base_w)
        scale_y = int(base_y * self.height / base_h)
        scaled = (scale_x, scale_y)
        logger.debug(f"Scaled coords: base=({base_x},{base_y}) -> {scaled}")
        return scaled
    
    def get_absolute_coords(self, base_x, base_y,
                          base_w=1920, base_h=1080):
        """Return _screen-relative_ coords, scaled to current size."""
        coords = self.get_scaled_coords(base_x, base_y, base_w, base_h)
        if not self.window:
            return (0, 0)
        scale_x = coords[0] + self.window['left'] 
        scale_y = coords[1] + self.window['top']
        absolute = (scale_x, scale_y)
        logger.debug(f"Absolute coords: base=({base_x},{base_y}) -> {absolute}")
        return absolute
    
    def make_screenshot(self):
        """Grab the full virtual screen, then crop to the window (original behavior)."""
        self.refresh_window_info()
        if not self.window:
            # Return a blank frame to prevent crashes when window is not available
            if self.last_screenshot is None:
                self.last_screenshot = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                self._last_frame_time = time.time()
            return self.last_screenshot
        with mss.mss() as sct:
            mon = sct.monitors[0]   # full virtual screen
            full = np.array(sct.grab(mon))[:, :, :3][:, :, ::-1]

        # compute window’s top-left _inside_ that full image
        left_in_full = self.window['left'] - mon['left']
        top_in_full  = self.window['top']  - mon['top']

        # slice out just the Arknights window
        w, h = self.width, self.height
        cropped = full[top_in_full: top_in_full + h,
                       left_in_full: left_in_full + w]

        self.last_screenshot = cropped
        self._last_frame_time = time.time()
        logger.debug(f"Screenshot captured: cropped size={cropped.shape}")
        return cropped

    def get_frame(self, fresh: bool = False):
        """Return a possibly cached frame; refresh if too old or requested fresh."""
        now = time.time()
        if (not fresh and self.last_screenshot is not None and
                (now - self._last_frame_time) * 1000.0 <= self._frame_max_age_ms):
            return self.last_screenshot
        return self.make_screenshot()

    def get_pixel_color(self, x, y):
        """Get the color of a pixel at (x, y) in the Arknights window."""
        screenshot = self.get_frame(fresh=False)
        x, y = self.get_scaled_coords(x, y)
        color = tuple(screenshot[y, x].tolist())
        logger.debug(f"Pixel color at ({x},{y}): {color}")
        return color

    # --- Robust color matching helpers (non-breaking; original API retained) ---
    def _color_distance(self, a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _roi_median_color(self, frame: np.ndarray, cx: int, cy: int, half: int) -> Tuple[int, int, int]:
        h, w, _ = frame.shape
        x1 = max(0, cx - half)
        y1 = max(0, cy - half)
        x2 = min(w - 1, cx + half)
        y2 = min(h - 1, cy + half)
        roi = frame[y1:y2 + 1, x1:x2 + 1]
        # median over ROI, return as RGB tuple
        med = np.median(roi.reshape(-1, 3), axis=0)
        return (int(med[0]), int(med[1]), int(med[2]))

    def check_color_at_robust(self, base_x, base_y, expected_rgb, confidence: Optional[float] = None):
        """Robust color check with ROI sampling and tolerance.

        This does not change the original check_color_at API; use this in new flows.
        """
        expected_rgb = tuple(expected_rgb)
        frame = self.get_frame(fresh=False)
        sx, sy = self.get_scaled_coords(base_x, base_y)
        half = Settings.colors.roi_half_size
        found_rgb = self._roi_median_color(frame, sx, sy, half)
        conf = Settings.colors.default_confidence if confidence is None else confidence
        if conf >= 1.0:
            return found_rgb == expected_rgb
        distance = self._color_distance(found_rgb, expected_rgb)
        max_distance = math.sqrt(3 * 255 ** 2)
        threshold = (1 - conf) * max_distance
        result = distance <= threshold
        logger.debug(f"Robust color check at ({base_x},{base_y}): found={found_rgb} expected={expected_rgb} dist={distance:.2f} thr={threshold:.2f} pass={result}")
        return result

    def check_color_at(self, base_x, base_y, expected_rgb, confidence=1):
        logger.debug(f"Checking color at base=({base_x},{base_y}), expected={expected_rgb}, confidence={confidence}")
        # Refresh window info before checking
        self.refresh_window_info()
        expected_rgb = tuple(expected_rgb)
        found_rgb = self.get_pixel_color(base_x, base_y)
        if confidence < 1:
            # Calculate color distance (0-255 per channel)
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(found_rgb, expected_rgb)))
            max_distance = math.sqrt(3 * 255 ** 2)  # Maximum possible distance
            
            # Convert confidence to threshold (higher confidence = lower threshold)
            threshold = (1 - confidence) * max_distance
            result = distance <= threshold
            logger.debug(f"Distance={distance:.2f}, threshold={threshold:.2f}, pass={result}")
            return result
            
        result = found_rgb == expected_rgb
        logger.debug(f"Exact match pass={result}")
        return result

    def click(self, base_x, base_y):
        """
        Clicks at the given base coordinates after converting them to absolute screen coordinates.
        
        Args:
            base_x (int): The base x-coordinate (relative to 1920x1080).
            base_y (int): The base y-coordinate (relative to 1920x1080).
        """
        if not self.window:
            logger.info("Click ignored: Arknights window not found")
            return
        absolute_coords = self.get_absolute_coords(base_x, base_y)
        logger.debug(f"Clicking at base coords ({base_x}, {base_y}) -> absolute {absolute_coords}")
        if self._dry_run:
            logger.info(f"[DRY-RUN] click at {absolute_coords}")
            return
        pg.click(*absolute_coords)

    # --- Ergonomic API ---
    def _jitter_coords(self, base_x: int, base_y: int) -> Tuple[int, int]:
        r = Settings.clicks.jitter_radius_px
        if r <= 0:
            return base_x, base_y
        return base_x + random.randint(-r, r), base_y + random.randint(-r, r)

    def _sleep_ms(self, ms: int):
        if ms > 0:
            time.sleep(ms / 1000.0)

    def should_abort(self) -> bool:
        if self._abort_flag:
            return True
        if Settings.safety.enable_panic_key:
            try:
                import keyboard  # optional dependency
                if keyboard.is_pressed(Settings.safety.panic_key):
                    return True
            except Exception:
                return False
        return False

    def set_abort(self, value: bool = True):
        self._abort_flag = bool(value)

    def is_visible(self, element_or_name: Union[UIElement, str], confidence: Optional[float] = None, use_single_pixel: bool = True, log_checks: bool = False) -> bool:
        el = element_or_name if isinstance(element_or_name, UIElement) else get_element(element_or_name)
        if not el:
            return False
        # Strategy 1: pixel points
        if el.pixel_points:
            ok = True
            for idx, (x, y, rgb) in enumerate(el.pixel_points, start=1):
                if use_single_pixel:
                    # default to exact if confidence not specified
                    conf = 1 if confidence is None else confidence
                    found_rgb = self.get_pixel_color(x, y)
                    passed = self.check_color_at(x, y, rgb, confidence=conf)
                else:
                    frame = self.get_frame(fresh=False)
                    sx, sy = self.get_scaled_coords(x, y)
                    found_rgb = self._roi_median_color(frame, sx, sy, Settings.colors.roi_half_size)
                    passed = self.check_color_at_robust(x, y, rgb, confidence=confidence)
                if log_checks:
                    status = "PASS" if passed else "FAIL"
                    name = getattr(el, 'name', str(element_or_name))
                    logger.debug(f"[{name}] check {idx} at ({x},{y}) expected={rgb} found={found_rgb} -> {status}")
                if not passed:
                    ok = False
                    break
            if ok:
                return True
        # Strategy 2: TODO template matching if template_path is provided
        # (left as future extension to avoid changing dependencies)
        return False

    def wait_visible(self, element_or_name: Union[UIElement, str], timeout: Optional[float] = None, use_single_pixel: bool = True) -> bool:
        waiter = Wait(timeout=timeout or Settings.timeouts.default_timeout,
                      name=f"wait_visible:{getattr(element_or_name, 'name', str(element_or_name))}",
                      abort_check=self.should_abort)
        return waiter.until(lambda: self.is_visible(element_or_name, use_single_pixel=use_single_pixel))

    def wait_gone(self, element_or_name: Union[UIElement, str], timeout: Optional[float] = None, use_single_pixel: bool = True) -> bool:
        waiter = Wait(timeout=timeout or Settings.timeouts.default_timeout,
                      name=f"wait_gone:{getattr(element_or_name, 'name', str(element_or_name))}",
                      abort_check=self.should_abort)
        return waiter.until(lambda: not self.is_visible(element_or_name, use_single_pixel=use_single_pixel))

    def tap(self, element_name: str, required: bool = True) -> bool:
        el = get_element(element_name)
        if not el:
            logger.warning(f"tap: element '{element_name}' not found in registry")
            return False
        if not self.window:
            logger.info("Tap ignored: Arknights window not found")
            return False
        # Prefer explicit click coords; if absent, fall back to first pixel anchor
        coords = el.click_coords or ((el.pixel_points[0][0], el.pixel_points[0][1]) if el.pixel_points else None)
        if not coords:
            logger.warning(f"tap: element '{element_name}' has no click coordinates")
            return False
        jx, jy = self._jitter_coords(coords[0], coords[1])
        abs_coords = self.get_absolute_coords(jx, jy)
        logger.debug(f"Tapping '{element_name}' at {abs_coords} (base {jx},{jy})")
        if self._dry_run:
            logger.info(f"[DRY-RUN] tap '{element_name}' at {abs_coords}")
            return True
        pg.click(*abs_coords)
        self._sleep_ms(Settings.clicks.post_click_grace_ms)
        return True

    def safe_click(self,
                   click: Union[Tuple[int, int], str],
                   expect_visible: Optional[str] = None,
                   timeout: Optional[float] = None) -> bool:
        """Click with jitter and verify expected visibility if provided.

        - click: base coords (x, y) or element name registered in elements.
        - expect_visible: element name to wait for after click.
        """
        if isinstance(click, str):
            ok = self.tap(click, required=False)
            if not ok:
                return False
        else:
            if not self.window:
                logger.info("safe_click ignored: Arknights window not found")
                return False
            jx, jy = self._jitter_coords(click[0], click[1])
            abs_coords = self.get_absolute_coords(jx, jy)
            logger.debug(f"safe_click at {abs_coords} (base {jx},{jy})")
            if self._dry_run:
                logger.info(f"[DRY-RUN] safe_click at {abs_coords}")
            else:
                pg.click(*abs_coords)
            self._sleep_ms(Settings.clicks.post_click_grace_ms)

        if expect_visible:
            return self.wait_visible(expect_visible, timeout=timeout)
        return True

    def click_and_wait(self, click_coords, wait_coords, expected_color, mode='appear', timeout=10, check_delay=0.01, confidence=0.9, use_single_pixel: bool = True):
        """
        Click at coordinates and wait for a color to appear/disappear.
        
        Args:
            click_coords: (x, y) base coordinates to click
            wait_coords: (x, y) base coordinates to monitor
            expected_color: RGB tuple to wait for
            mode: 'appear' or 'disappear'
            timeout: Maximum time to wait
            check_delay: Delay between checks
            confidence: Color matching confidence
        """
        # Click (jittered) and wait using robust checks
        jx, jy = self._jitter_coords(click_coords[0], click_coords[1])
        absolute_coords = self.get_absolute_coords(jx, jy)
        logger.debug(f"Clicking at {absolute_coords} and waiting for {expected_color} to {mode} at {wait_coords}")
        if self._dry_run:
            logger.info(f"[DRY-RUN] click at {absolute_coords}")
        else:
            pg.click(*absolute_coords)
        self._sleep_ms(Settings.clicks.post_click_grace_ms)

        # Wait for response (resilient)
        def predicate():
            if use_single_pixel:
                ok = self.check_color_at(*wait_coords, expected_color, confidence=1 if confidence is None else confidence)
            else:
                ok = self.check_color_at_robust(*wait_coords, expected_color, confidence=max(confidence, Settings.colors.default_confidence))
            return ok if mode == 'appear' else (not ok)

        waiter = Wait(timeout=timeout, name=f"click_and_wait:{mode}", abort_check=self.should_abort)
        ok = waiter.until(predicate)
        if not ok and Settings.observability.enable_failure_screenshots:
            try:
                x, y = self.get_scaled_coords(wait_coords[0], wait_coords[1])
                self.save_failure_artifact(f"click_and_wait_timeout_{mode}", roi_rects=[(x-10, y-10, 20, 20)])
            except Exception:
                pass
        return ok

    def wait_for_color_change(self, coords, expected_color, mode='appear', timeout=10, check_delay=0.01, confidence=0.9, use_single_pixel: bool = True):
        """Wait for a color to appear/disappear without clicking (resilient)."""
        logger.debug(f"Waiting for {expected_color} to {mode} at {coords}")

        def predicate():
            if use_single_pixel:
                ok = self.check_color_at(*coords, expected_color, confidence=1 if confidence is None else confidence)
            else:
                ok = self.check_color_at_robust(*coords, expected_color, confidence=max(confidence, Settings.colors.default_confidence))
            return ok if mode == 'appear' else (not ok)

        waiter = Wait(timeout=timeout, name=f"wait_for_color_change:{mode}", abort_check=self.should_abort)
        ok = waiter.until(predicate)
        if not ok and Settings.observability.enable_failure_screenshots:
            try:
                x, y = self.get_scaled_coords(coords[0], coords[1])
                self.save_failure_artifact(f"wait_for_color_change_timeout_{mode}", roi_rects=[(x-10, y-10, 20, 20)])
            except Exception:
                pass
        return ok

    def spam_click_until_color(self, click_coords, wait_coords, expected_color, mode='appear', timeout=10, click_delay=0.5, confidence=1, use_single_pixel: bool = True):
        """
        Repeatedly click at coordinates until a color appears/disappears at another location.
        
        Args:
            click_coords: (x, y) base coordinates to click repeatedly
            wait_coords: (x, y) base coordinates to monitor
            expected_color: RGB tuple to wait for
            mode: 'appear' or 'disappear'
            timeout: Maximum time to wait
            click_delay: Delay between each click
            confidence: Color matching confidence
        """
        start_time = time.time()
        logger.debug(f"Spam clicking {click_coords} until color {expected_color} to {mode} at {wait_coords}")

        def condition_met() -> bool:
            if use_single_pixel:
                ok = self.check_color_at(*wait_coords, expected_color, confidence=1 if confidence is None else confidence)
            else:
                ok = self.check_color_at_robust(*wait_coords, expected_color, confidence=max(confidence, Settings.colors.default_confidence))
            return ok if mode == 'appear' else (not ok)

        if condition_met():
            logger.debug("Color condition met before starting spam click.")
            return True

        while time.time() - start_time < timeout:
            jx, jy = self._jitter_coords(click_coords[0], click_coords[1])
            absolute_coords = self.get_absolute_coords(jx, jy)
            if self._dry_run:
                logger.info(f"[DRY-RUN] spam-click at {absolute_coords}")
            else:
                pg.click(*absolute_coords)
            self._sleep_ms(int(click_delay * 1000))

            if condition_met():
                logger.debug(f"Color changed after {time.time() - start_time:.2f}s")
                return True
            if self.should_abort():
                logger.warning("spam_click_until_color aborted by panic/safety signal")
                return False

        logger.warning(f"Timeout spam clicking for color to {mode}")
        if Settings.observability.enable_failure_screenshots:
            try:
                x, y = self.get_scaled_coords(wait_coords[0], wait_coords[1])
                self.save_failure_artifact(f"spam_click_timeout_{mode}", roi_rects=[(x-10, y-10, 20, 20)])
            except Exception:
                pass
        return False

    # --- State wrappers ---
    def wait_state(self, state_name: str, timeout: Optional[float] = None) -> bool:
        return _states.wait_state(self, state_name, timeout=timeout)

    # --- Observability ---
    def save_failure_artifact(self, label: str, roi_rects: Optional[List[Tuple[int, int, int, int]]] = None) -> Optional[str]:
        try:
            frame = self.get_frame(fresh=True)  # RGB numpy array
            img = Image.fromarray(frame)
            if roi_rects:
                draw = ImageDraw.Draw(img)
                # Convert configured BGR to RGB for PIL if needed
                b, g, r = Settings.observability.annotation_color_bgr
                color_rgb = (r, g, b)
                for (x, y, w, h) in roi_rects:
                    draw.rectangle([x, y, x + w, y + h], outline=color_rgb, width=Settings.observability.annotation_thickness_px)
            ts = int(time.time() * 1000)
            dir_path = os.path.join(os.path.dirname(__file__), Settings.observability.artifacts_dir_name)
            os.makedirs(dir_path, exist_ok=True)
            path = os.path.join(dir_path, f"artifact_{label}_{ts}.png")
            img.save(path)
            logger.info(f"Saved failure artifact: {path}")
            return path
        except Exception as ex:
            logger.warning(f"Failed to save failure artifact: {ex}")
            return None

ark_window = ArknightsWindow('BlueStacks App Player')
if __name__ == "__main__":
    # print([w.title for w in gw.getAllWindows() if 'bluestacks' in w.title.lower()])
    # coords = ark_window.get_scaled_coords(486, 435)
    # screen_coords = ark_window.get_absolute_coords(486, 435)
    # logger.debug(f"Example coords: scaled={coords}, absolute={screen_coords}")
    # logger.debug(f"Color check example: {ark_window.check_color_at(*coords, (255, 255, 255))}")
    # logger.debug(f"Pixel color example: {ark_window.get_pixel_color(*coords)}")
    print(get_arknights_window_title())