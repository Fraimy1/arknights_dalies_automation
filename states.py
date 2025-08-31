from typing import Optional
from config import Settings
from elements import get_element


# Minimal screen state identifiers
MAIN_MENU = "main_menu"
RECRUITMENT_PANEL = "recruitment_panel"
BASE_PANEL = "base_panel"
MISSIONS_PANEL = "missions_panel"
FRIENDS_PANEL = "friends_panel"
TERMINAL_PANEL = "terminal_panel"
STORE_PANEL = "store_panel"

def get_state_indicator_element_name(state_name: str) -> Optional[str]:
    if state_name == MAIN_MENU:
        return "main_menu_indicators"
    if state_name == RECRUITMENT_PANEL:
        return "recruitment_indicator"
    if state_name == BASE_PANEL:
        return "base_indicator"
    if state_name == MISSIONS_PANEL:
        return "missions_indicators"
    if state_name == FRIENDS_PANEL:
        return "friends_indicator"
    if state_name == TERMINAL_PANEL:
        return "terminal_indicator"
    if state_name == STORE_PANEL:
        return "recommended_store_indicator"
    return None

def is_state(window, state_name: str) -> bool:
    if state_name == MAIN_MENU:
        el = get_element("main_menu_indicators")
        return window.is_visible(el, log_checks=True) if el else False
    if state_name == RECRUITMENT_PANEL:
        el = get_element("recruitment_indicator")
        return window.is_visible(el, log_checks=True) if el else False
    if state_name == BASE_PANEL:
        el = get_element("base_indicator")
        return window.is_visible(el, log_checks=True) if el else False
    if state_name == MISSIONS_PANEL:
        el = get_element("missions_indicators")
        return window.is_visible(el, log_checks=True) if el else False
    if state_name == FRIENDS_PANEL:
        el = get_element("friends_indicator")
        return window.is_visible(el, log_checks=True) if el else False
    if state_name == TERMINAL_PANEL:
        el = get_element("terminal_indicator")
        return window.is_visible(el, log_checks=True) if el else False
    if state_name == STORE_PANEL:
        el = get_element("recommended_store_indicator")
        return window.is_visible(el, log_checks=True) if el else False
    return False


def wait_state(window, state_name: str, timeout: Optional[float] = None) -> bool:
    from waits import Wait
    t = Settings.timeouts
    waiter = Wait(timeout=timeout or t.default_timeout, name=f"wait_state:{state_name}", abort_check=window.should_abort)
    return waiter.until(lambda: is_state(window, state_name))


