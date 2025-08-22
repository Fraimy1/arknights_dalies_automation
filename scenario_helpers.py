from typing import Optional
from logger import logger
from config import Settings
from states import MAIN_MENU, wait_state


def recover_to_main_menu(window, max_attempts: int = 3) -> bool:
    """Best-effort recovery to main menu.

    This uses configured elements (if available) and conservative heuristics. It does not
    change scenario logic; call this when a step times out to try returning to a known state.
    """
    logger.info("Attempting to recover to main menu...")

    # Try pressing ESC/back a few times to close modals/popups (if emulator forwards it)
    try:
        import pyautogui as pg
        for _ in range(max_attempts):
            if wait_state(window, MAIN_MENU, timeout=1.0):
                logger.info("Already at main menu.")
                return True
            pg.press('esc')
    except Exception:
        pass

    # If a specific element or coordinate for 'home' exists, tap it (placeholder via ergonomic API)
    for _ in range(max_attempts):
        if wait_state(window, MAIN_MENU, timeout=1.0):
            return True
        if hasattr(window, 'tap'):
            try:
                # You can add a named element 'home_button' to elements.py later
                window.tap('home_button', required=False)
            except Exception:
                break

    # Final check
    ok = wait_state(window, MAIN_MENU, timeout=Settings.timeouts.short_timeout)
    if ok:
        logger.info("Recovered to main menu.")
    else:
        logger.warning("Failed to recover to main menu.")
    return ok


