import pyautogui
import time

def click(x, y, clicks=1, interval=0.1):
    """
    Clicks at the specified coordinates.

    Args:
        x (int): The x-coordinate.
        y (int): The y-coordinate.
        clicks (int): The number of clicks to perform.
        interval (float): The interval between clicks.
    """
    pyautogui.click(x, y, clicks=clicks, interval=interval)

def locate_and_click(image, confidence=0.8, clicks=1, interval=0.1):
    """
    Locates an image on the screen and clicks on it.

    Args:
        image (str): The path to the image file.
        confidence (float): The confidence level for image matching.
        clicks (int): The number of clicks to perform.
        interval (float): The interval between clicks.
    """
    try:
        location = pyautogui.locateCenterOnScreen(image, confidence=confidence)
        if location:
            click(location.x, location.y, clicks=clicks, interval=interval)
            return True
    except pyautogui.ImageNotFoundException:
        return False
    return False

def get_window_geometry(window_title="Arknights"):
    """
    Gets the geometry of the specified window.

    Args:
        window_title (str): The title of the window to find.

    Returns:
        tuple: A tuple containing (x, y, width, height) of the window, or None if not found.
    """
    try:
        window = pyautogui.getWindowsWithTitle(window_title)[0]
        return window.left, window.top, window.width, window.height
    except IndexError:
        print(f"Window with title '{window_title}' not found.")
        return None

def transform_coordinates(x, y, window_geometry):
    """
    Transforms fullscreen coordinates to window-relative coordinates.

    Args:
        x (int): The x-coordinate in fullscreen.
        y (int): The y-coordinate in fullscreen.
        window_geometry (tuple): A tuple containing (x, y, width, height) of the window.

    Returns:
        tuple: A tuple containing the transformed (x, y) coordinates.
    """
    if not window_geometry:
        return x, y
    
    win_x, win_y, _, _ = window_geometry
    return x + win_x, y + win_y
