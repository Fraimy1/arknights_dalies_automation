import re

from PIL.ImageChops import screen
from time import sleep
import pyautogui as pg
import pygetwindow as gw
import mss
import numpy as np
import math

def get_arknights_window_title(keywords_to_exclude=[]):
    """Get the title of the Arknights window."""
    windows = gw.getAllWindows()
    keywords_to_exclude.append('arknights_dalies_automation')
    windows = [w for w in windows if "arknights" in w.title.lower().strip() \
               and not any(name for name in keywords_to_exclude if name in w.title.lower().strip())]

    if windows:
        return windows[0].title
    return None

def get_window_info(window_title):
    """Get the position and size of a window by its title."""
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        return None
    window = windows[0]
    return {
        'left': window.left,
        'right': window.right,
        'top': window.top,
        'bottom': window.bottom,
        'width': window.width,
        'height': window.height,
        'title': window.title
    }

arknights_title = get_arknights_window_title()
print(arknights_title)
print(get_window_info(arknights_title))

windowed_offsets = {
    'google_play': (9, 8, 31, 8)
}

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

    def refresh_window_info(self):
        """Refresh window information in case window moved/resized."""
        self.window = get_window_info(self.title)
        if self.window:
            self.width = self.window['width']
            self.height = self.window['height']

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
        return scale_x, scale_y
    
    def get_screen_coords(self, base_x, base_y,
                          base_w=1920, base_h=1080):
        """Return _screen-relative_ coords, scaled to current size."""
        coords = self.get_scaled_coords(base_x, base_y, base_w, base_h)
        scale_x = coords[0] + self.window['left'] 
        scale_y = coords[1] + self.window['top']
        return scale_x, scale_y
    
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
        return cropped

    def get_pixel_color(self, x, y):
        """x, y must now be window-relative coords—just index into cropped."""
        screenshot = self.make_screenshot()
        return tuple(screenshot[y, x].tolist())

    def check_color_at(self, base_x, base_y, expected_rgb, confidence=1):
        # Refresh window info before checking
        self.refresh_window_info()
        expected_rgb = tuple(expected_rgb)
        found_rgb = self.get_pixel_color(*self.get_scaled_coords(base_x, base_y))
        if confidence < 1:
            # Calculate color distance (0-255 per channel)
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(found_rgb, expected_rgb)))
            max_distance = math.sqrt(3 * 255 ** 2)  # Maximum possible distance
            
            # Convert confidence to threshold (higher confidence = lower threshold)
            threshold = (1 - confidence) * max_distance
            return distance <= threshold
            
        return found_rgb == expected_rgb


ark_window = ArknightsWindow()
coords = ark_window.get_scaled_coords(486, 435)
screen_coords = ark_window.get_screen_coords(486, 435)
print(coords, screen_coords)  # Example usage

print(ark_window.check_color_at(*coords, (255, 255, 255)))

print(ark_window.get_pixel_color(*coords))  # Example usage
