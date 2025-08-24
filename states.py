from typing import Optional
from config import Settings
from elements import get_element


# Minimal screen state identifiers
MAIN_MENU = "main_menu"
RECRUITMENT_PANEL = "recruitment_panel"
BASE_PANEL = "base_panel"

def is_state(window, state_name: str) -> bool:
    if state_name == MAIN_MENU:
        el = get_element("main_menu_confirm_points")
        return window.is_visible(el) if el else False
    if state_name == RECRUITMENT_PANEL:
        el = get_element("recruitment_panel_indicator")
        return window.is_visible(el) if el else False
    if state_name == BASE_PANEL:
        el = get_element("base_panel_indicator")
        return window.is_visible(el) if el else False
    return False


def wait_state(window, state_name: str, timeout: Optional[float] = None) -> bool:
    from waits import Wait
    t = Settings.timeouts
    waiter = Wait(timeout=timeout or t.default_timeout, name=f"wait_state:{state_name}", abort_check=window.should_abort)
    return waiter.until(lambda: is_state(window, state_name))


