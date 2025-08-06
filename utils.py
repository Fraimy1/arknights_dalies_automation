from os import name
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
    logger.debug(f"Entering get_window_info with title: {window_title}")
    """Get the position and size of a window by its title, preferring an exact match."""
    if not window_title:
        logger.warning("get_window_info called with an empty title.")
        return None

    windows = gw.getWindowsWithTitle(window_title)
    logger.debug(f"Found potential windows: {[w.title for w in windows]} for title '{window_title}'")

    # Prefer an exact match to avoid ambiguity
    for window in windows:
        if window.title == window_title:
            logger.debug(f"Found exact match: {window.title}")
            info = {
                'left': window.left,
                'right': window.right,
                'top': window.top,
                'bottom': window.bottom,
                'width': window.width,
                'height': window.height,
                'title': window.title
            }
            logger.debug(f"Window info: {info}")
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
        self.width = self.window['width']
        self.height = self.window['height']
        self.last_screenshot = None
        self.is_windowed = False

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
        logger.debug(f"Refreshing window info for title: {self.title}")
        old_size = (self.width, self.height)
        self.window = get_window_info(self.title)
        if self.window:
            self.width = self.window['width']
            self.height = self.window['height']
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
        scale_x = coords[0] + self.window['left'] 
        scale_y = coords[1] + self.window['top']
        absolute = (scale_x, scale_y)
        logger.debug(f"Absolute coords: base=({base_x},{base_y}) -> {absolute}")
        return absolute
    
    def make_screenshot(self):
        """Grab the full virtual screen, then crop to the window."""
        self.refresh_window_info()
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
        logger.debug(f"Screenshot captured: cropped size={cropped.shape}")
        return cropped

    def get_pixel_color(self, x, y):
        """Get the color of a pixel at (x, y) in the Arknights window."""
        screenshot = self.make_screenshot()
        x, y = self.get_scaled_coords(x, y)
        color = tuple(screenshot[y, x].tolist())
        logger.debug(f"Pixel color at ({x},{y}): {color}")
        return color

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
        absolute_coords = self.get_absolute_coords(base_x, base_y)
        logger.debug(f"Clicking at base coords ({base_x}, {base_y}) -> absolute {absolute_coords}")
        pg.click(*absolute_coords)

    def click_and_wait(self, click_coords, wait_coords, expected_color, mode='appear', timeout=10, check_delay=0.01, confidence=0.9):
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
        # Click
        absolute_coords = self.get_absolute_coords(*click_coords)
        logger.debug(f"Clicking at {absolute_coords} and waiting for {expected_color} to {mode} at {wait_coords}")
        pg.click(*absolute_coords)
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            color_present = self.check_color_at(*wait_coords, expected_color, confidence=confidence)
            
            if mode == 'appear' and color_present:
                logger.debug(f"Color appeared after {time.time() - start_time:.2f}s")
                return True
            elif mode == 'disappear' and not color_present:
                logger.debug(f"Color disappeared after {time.time() - start_time:.2f}s")
                return True
                
            sleep(check_delay)
        
        logger.warning(f"Timeout waiting for color to {mode}")
        return False

    def wait_for_color_change(self, coords, expected_color, mode='appear', timeout=10, check_delay=0.01, confidence=0.9):
        """Wait for a color to appear/disappear without clicking."""
        start_time = time.time()
        logger.debug(f"Waiting for {expected_color} to {mode} at {coords}")
        
        while time.time() - start_time < timeout:
            color_present = self.check_color_at(*coords, expected_color, confidence=confidence)
            
            if mode == 'appear' and color_present:
                logger.debug(f"Color appeared after {time.time() - start_time:.2f}s")
                return True
            elif mode == 'disappear' and not color_present:
                logger.debug(f"Color disappeared after {time.time() - start_time:.2f}s")
                return True
                
            sleep(check_delay)
        
        logger.warning(f"Timeout waiting for color to {mode}")
        return False

    def spam_click_until_color(self, click_coords, wait_coords, expected_color, mode='appear', timeout=10, click_delay=0.5, confidence=0.9):
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

        while time.time() - start_time < timeout:
            # First, check if the condition is already met before clicking
            color_present = self.check_color_at(*wait_coords, expected_color, confidence=confidence)
            if (mode == 'appear' and color_present) or (mode == 'disappear' and not color_present):
                logger.debug(f"Color condition met before starting spam click.")
                return True

            # If not, click and wait
            absolute_coords = self.get_absolute_coords(*click_coords)
            pg.click(*absolute_coords)
            logger.debug(f"Clicked at {absolute_coords}, waiting for {click_delay}s")
            sleep(click_delay)

            # Check again after clicking
            color_present = self.check_color_at(*wait_coords, expected_color, confidence=confidence)
            if (mode == 'appear' and color_present):
                logger.debug(f"Color appeared after {time.time() - start_time:.2f}s")
                return True
            elif (mode == 'disappear' and not color_present):
                logger.debug(f"Color disappeared after {time.time() - start_time:.2f}s")
                return True

        logger.warning(f"Timeout spam clicking for color to {mode}")
        return False

ark_window = ArknightsWindow()
if __name__ == "__main__":
    # coords = ark_window.get_scaled_coords(486, 435)
    # screen_coords = ark_window.get_absolute_coords(486, 435)
    # logger.debug(f"Example coords: scaled={coords}, absolute={screen_coords}")
    # logger.debug(f"Color check example: {ark_window.check_color_at(*coords, (255, 255, 255))}")
    # logger.debug(f"Pixel color example: {ark_window.get_pixel_color(*coords)}")
    print(get_arknights_window_title())