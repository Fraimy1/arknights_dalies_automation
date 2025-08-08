from cv2 import exp
from utils import ArknightsWindow, ark_window
from time import sleep
from logger import logger
import pyautogui as pg
# Physical: X=3323,Y=266; Scaled: X=3323,Y=266; Relative: X=763,Y=578; Dpi: 96; Raw Dpi: 81; Dpi Ratio: 1,19; Screen Resolution: 1920x1080; Pixel Color: #313131
# Physical: X=3579,Y=263; Scaled: X=3579,Y=263; Relative: X=1019,Y=575; Dpi: 96; Raw Dpi: 81; Dpi Ratio: 1,19; Screen Resolution: 1920x1080; Pixel Color: #313131
# Physical: X=3829,Y=264; Scaled: X=3829,Y=264; Relative: X=1269,Y=576; Dpi: 96; Raw Dpi: 81; Dpi Ratio: 1,19; Screen Resolution: 1920x1080; Pixel Color: #313131
# Physical: X=3327,Y=372; Scaled: X=3327,Y=372; Relative: X=767,Y=684; Dpi: 96; Raw Dpi: 81; Dpi Ratio: 1,19; Screen Resolution: 1920x1080; Pixel Color: #313131
# Physical: X=3575,Y=369; Scaled: X=3575,Y=369; Relative: X=1015,Y=681; Dpi: 96; Raw Dpi: 81; Dpi Ratio: 1,19; Screen Resolution: 1920x1080; Pixel Color: #313131
recruitment_status_coords = {
    1: (763, 578),
    2: (1019, 575),
    3: (1269, 576),
    4: (767, 684),
    5: (1015, 681),
}
class DailyRecruits:
    """
    This class automates the daily recruitment process in Arknights.
    """
    
    def __init__(self, use_expedite=False, finish_on_recruitment=True):
        self.coords = {
            1: (486, 435),
            2: (1433, 435),
            3: (486, 851),
            4: (1433, 851),
        }
        self.use_expedite = use_expedite
        self.finish_on_recruitment = finish_on_recruitment
        logger.debug(f"DailyRecruits initialized: expedite={self.use_expedite}, finish_on_recruitment={self.finish_on_recruitment}")

    def _click_recruitment_tile(self, n: int):
        """Clicks the nth recruitment tile (1–4)."""
        coords = self.coords[n]
        logger.debug(f"Clicking recruitment tile {n} at {coords}")
        ark_window.click_and_wait(coords, (1460, 860), (255, 255, 255), mode='appear', timeout=5)

    def _refresh_available(self):
        """Check if the refresh button is available."""
        coords = (1450, 604)
        is_available = ark_window.check_color_at(*coords, (0, 153, 220), confidence=1)
        logger.debug(f"Refresh button available: {is_available}")
        return is_available

    def _click_refresh_button(self):
        """Click the refresh button to refresh the recruitment options."""
        coords = (1450, 604)
        logger.debug(f"Clicking refresh button at {coords}")
        ark_window.click_and_wait(coords, (1260, 727), (255, 255, 255), mode='appear', timeout=5)
        ark_window.spam_click_until_color((1260, 727), (1260, 727), (255, 255, 255), mode='disappear', timeout=5)  # Confirm refresh

    def rare_option_available(self):
        """Check the recruitment options to see if they match desired criteria."""
        for i in range(1, 6):
            coords = recruitment_status_coords[i]
            if not ark_window.check_color_at(*coords, (49, 49, 49), confidence=1):
                logger.debug(f"Recruitment option {i} is rare")
                return True
            else:
                logger.debug(f"Recruitment option {i} is common")
        return False

    def _click_hiring_tile(self, i):
        """Click the hiring tile to start the recruitment process."""
        coords = self.coords[i][0], self.coords[i][1]+136
        logger.debug(f"Clicking hiring tile {i} at {coords}")
        ark_window.spam_click_until_color(coords, (1833, 51), (255, 255, 255), mode='appear', timeout=5)

    def _skip_button(self):
        """Click the skip button to skip the hiring animation."""
        logger.debug("Waiting for skip button to appear and clicking it")
        
        # Wait for skip button to appear, then click and wait for main UI to return
        if ark_window.wait_for_color_change((1833, 51), (255, 255, 255), mode='appear', timeout=10):
            ark_window.click_and_wait((1833, 51), (847, 120), (255, 255, 255), mode='disappear', timeout=10)
        else:
            logger.warning("Skip button never appeared, continuing anyway")

        ark_window.spam_click_until_color((1833, 51), (1717, 52), (255, 255, 255), mode='appear', timeout=15)
        
    def check_tile(self, i):
        """Check the status of the hiring tile."""        
        logger.debug(f"Checking tile status for tile {i}")
        is_plus = ark_window.check_color_at(*self.coords[i], (255, 255, 255), confidence=1)

        # There are only 3 states in which recruitment can be:
        # 1. No recruitment in progress (plus sign)
        # 2. Recruitment in progress (recruitment permit is on the screen)
        # 3. Recruitment done (Any other color in place of recruitment permit)
        if is_plus:
            logger.debug(f"Tile {i} status: no_recruitment")
            return 'no_recruitment'
        else:
            recruitment_permit_coords = ark_window.get_scaled_coords(self.coords[i][0]-105, self.coords[i][1]+25)
            recruitment_in_progress = ark_window.check_color_at(*recruitment_permit_coords, (255, 255, 255), confidence=1)

            if recruitment_in_progress:
                logger.debug(f"Tile {i} status: recruitment_in_progress")
                return 'recruitment_in_progress'
            else:
                logger.debug(f"Tile {i} status: recruitment_done")
                return 'recruitment_done'
    
    def _confirm_recruitment(self, i):
        """Confirm recruitment by setting time to 9h and confirming."""
        logger.debug(f"Confirming recruitment for tile {i}")
        
        # Set time to 9h, then confirm recruitment, then wait for loading to finish
        ark_window.click(674, 449)
        ark_window.spam_click_until_color((1463, 876), (1539, 865), (0, 153, 220), mode='disappear', timeout=10)

    def _do_expedite(self, i):
        """Use expedite to speed up the recruitment process."""
        expedite_coords = (self.coords[i][0]+220, self.coords[i][1]+145)
        logger.debug(f"Expediting recruitment for tile {i}")
        
        # Click expedite button and wait for confirmation dialog, then confirm
        ark_window.spam_click_until_color(expedite_coords, (1432, 748), (255, 255, 255), mode='appear', timeout=5)
        ark_window.spam_click_until_color((1432, 748), (1432, 748), (255, 255, 255), mode='disappear', timeout=3)
        
    def do_recruitment(self):
        """Perform a full recruitment cycle."""
        logger.info("Starting daily recruitment scenario...")
        for i in range(1, 5):
            logger.debug(f"Recruitment cycle for tile {i}")
            self._click_recruitment_tile(i)
            self._confirm_recruitment(i)

    def do_daily_recruits(self):
        """Main method to execute the daily recruitment scenario based on chosen mode."""
        for i in range(1, 5):
            tile_status = self.check_tile(i)
            logger.info(f"Tile {i} status: {tile_status} in main loop")
            if tile_status == 'no_recruitment':
                self._click_recruitment_tile(i)
                while self._refresh_available() and not self.rare_option_available():
                   logger.info(f"Refresh available for tile {i}")
                   self._click_refresh_button()

                if self.rare_option_available():
                    logger.info(f"Rare recruitment option available for tile {i}")
                    ark_window.click_and_wait((1461, 955), (1461, 955), (255, 255, 255), mode='disappear', timeout=5)
                    continue

                self._confirm_recruitment(i)
            elif tile_status == 'recruitment_in_progress':
                if not self.use_expedite:
                    logger.info(f"Recruitment in progress for tile {i}. Skipping expedite.")
                    continue
                self._do_expedite(i)
                self._click_hiring_tile(i)
                self._skip_button()

                if self.finish_on_recruitment:
                    self._click_recruitment_tile(i)
                    while self._refresh_available() and not self.rare_option_available():
                        logger.info(f"Refresh available for tile {i}")
                        self._click_refresh_button()

                    if self.rare_option_available():
                        logger.info(f"Rare recruitment option available for tile {i}")
                        ark_window.click_and_wait((1461, 955), (1461, 955), (255, 255, 255), mode='disappear', timeout=5)
                        continue

                    logger.info(f"Finish on recruitment: final cycle for tile {i}")
                    self._confirm_recruitment(i)
            elif tile_status == 'recruitment_done':
                self._click_hiring_tile(i)
                self._skip_button()

class MainMenu:
    """
    This class automates the main menu process in Arknights.
    """

    def __init__(self):
        self.tile_coords = { 
            'recruit': (1500, 760),
            'headhunt': (1760, 760),
            'store': (1300, 720),
            'missions': (1200, 900),
            'base': (1550, 950),
            'terminal': (1450, 250),
            'friends': (540, 850),
        }

        self.return_coords = {
            'recruit': []
        }
    
    def click_tile(self, tile_name):
        """Click the tile with the given name."""
        coords = self.tile_coords[tile_name]
        logger.debug(f"Clicking tile {tile_name} at {coords}")
        ark_window.click(*coords)

    def is_main_menu_visible(self):
        """Check if the main menu is visible."""
        return ark_window.check_color_at(1355, 110, (255, 255, 255), confidence=1)

    def open_main_menu(self):
        """Open the main menu."""
        ark_window.click_and_wait((400, 50), (1421, 405), (255, 255, 255), mode='appear', timeout=5)
        ark_window.click(130, 118)

if __name__ == "__main__":
    daily_recruits = DailyRecruits(use_expedite=False)
    # daily_recruits.do_hiring()
    daily_recruits.do_daily_recruits()
    # logger.info("Daily recruitment scenario completed.")
    # status = daily_recruits.check_tile(1)
    # print(f"Tile 1 status: {status}")
    # if status == 'recruitment_in_progress':
    #     daily_recruits._do_expedite(1)
    #     sleep(2)
    #     daily_recruits._click_hiring_tile(1)
    #     daily_recruits._skip_button()