from config import Settings
from utils import ark_window
from states import get_state_indicator_element_name, STORE_PANEL, CREDIT_STORE_PANEL
from elements import get_element
from time import sleep
from logger import logger
class DailyRecruits:
    """
    This class automates the daily recruitment process in Arknights.
    """
    
    def __init__(self, use_expedite=False, finish_on_recruitment=True):
        self.use_expedite = use_expedite
        self.finish_on_recruitment = finish_on_recruitment
        logger.debug(f"DailyRecruits initialized: expedite={self.use_expedite}, finish_on_recruitment={self.finish_on_recruitment}")

    def _click_recruitment_tile(self, n: int):
        """Clicks the nth recruitment tile (1–4)."""
        tile_element_name = f"recruitment_tile_{n}"
        tile_coords = get_element(tile_element_name).click_coords
        logger.debug(f"Clicking recruitment tile {n} at {tile_coords}")
        ark_window.tap(tile_element_name)
        ark_window.wait_visible('recruitment_panel_indicator', timeout=5)

    def _refresh_available(self):
        """Check if the refresh button is available."""
        refresh_button = get_element('recruit_refresh_button')
        refresh_button_coords = refresh_button.click_coords
        refresh_button_color = refresh_button.pixel_points[0][2]
        is_available = ark_window.check_color_at(*refresh_button_coords, refresh_button_color, confidence=1)
        logger.debug(f"Refresh button available: {is_available}")
        return is_available

    def _click_refresh_button(self):
        """Click the refresh button to refresh the recruitment options."""
        refresh_button = get_element('recruit_refresh_button')
        refresh_confirm = get_element('recruit_refresh_confirm')
        logger.debug(f"Clicking refresh button at {refresh_button.click_coords}")
        ark_window.tap('recruit_refresh_button')
        ark_window.wait_visible('recruit_refresh_confirm', timeout=5)
        ark_window.tap('recruit_refresh_confirm')
        ark_window.wait_gone('recruit_refresh_confirm', timeout=5)

    def rare_option_available(self):
        """Check the recruitment tag rows; non-(49,49,49) indicates rare."""
        for i in range(1, 6):
            recruitment_tag_element = get_element(f'recruitment_tag_{i}')
            recruitment_tag_coords = recruitment_tag_element.click_coords
            recruitment_tag_common_color = recruitment_tag_element.pixel_points[0][2]
            if not ark_window.check_color_at(*recruitment_tag_coords, recruitment_tag_common_color, confidence=1):
                logger.debug(f"Recruitment option {i} is rare")
                return True
            logger.debug(f"Recruitment option {i} is common")
        return False

    def _click_hiring_tile(self, i):
        """Click the hiring tile to start the recruitment process."""
        hiring_tile_element_name = f"hiring_tile_{i}"
        hiring_tile_coords = get_element(hiring_tile_element_name).click_coords
        logger.debug(f"Clicking hiring tile {i} at {hiring_tile_coords}")
        ark_window.tap(hiring_tile_element_name)
        ark_window.wait_visible('skip_button_anchor', timeout=5)

    def _skip_button(self):
        """Click the skip button to skip the hiring animation."""
        logger.debug("Waiting for skip button to appear and clicking it")
        if ark_window.wait_visible('skip_button_anchor', timeout=10):
            ark_window.tap('skip_button_anchor')
            ark_window.wait_gone('post_skip_wait_point', timeout=10)
        else:
            logger.warning("Skip button never appeared, continuing anyway")
        recruitment_indicator_coords = get_element('recruitment_indicator').pixel_points[0][:2]
        recruitment_indicator_color = get_element('recruitment_indicator').pixel_points[0][2]
        ark_window.spam_click_until_color(
            click_coords=recruitment_indicator_coords,
            wait_coords=recruitment_indicator_coords,
            expected_color=recruitment_indicator_color,
            mode='appear',
            timeout=20,
        )

    def check_tile(self, i):
        """Check the status of the hiring tile."""        
        logger.debug(f"Checking tile status for tile {i}")
        tile_center_element_name = f"recruitment_tile_{i}"
        tile_center_coords = get_element(tile_center_element_name).click_coords
        is_plus = ark_window.check_color_at(*tile_center_coords, (255, 255, 255), confidence=1)

        # There are only 3 states in which recruitment can be:
        # 1. No recruitment in progress (plus sign)
        # 2. Recruitment in progress (recruitment permit is on the screen)
        # 3. Recruitment done (Any other color in place of recruitment permit)
        if is_plus:
            logger.debug(f"Tile {i} status: no_recruitment")
            return 'no_recruitment'
        else:
            permit_element_name = f"recruitment_permit_{i}"
            permit_coords = get_element(permit_element_name).click_coords
            recruitment_in_progress = ark_window.check_color_at(*permit_coords, (255, 255, 255), confidence=1)

            if recruitment_in_progress:
                logger.debug(f"Tile {i} status: recruitment_in_progress")
                return 'recruitment_in_progress'
            else:
                logger.debug(f"Tile {i} status: recruitment_done")
                return 'recruitment_done'
        
    def _confirm_recruitment(self, i):
        """Confirm recruitment by setting time to 9h and confirming."""
        logger.debug(f"Confirming recruitment for tile {i}")
        ark_window.tap('recruit_confirm_button_top')
        ark_window.tap('recruit_confirm_button_bottom')
        ark_window.wait_gone('recruit_confirm_state_pixel', timeout=10)

    def _do_expedite(self, i):
        """Use expedite to speed up the recruitment process."""
        expedite_button_element_name = f'expedite_button_{i}'
        logger.debug(f"Expediting recruitment for tile {i}")
        
        # Click expedite button and wait for confirmation dialog, then confirm
        ark_window.tap(expedite_button_element_name)
        if ark_window.wait_visible('expedite_confirm', timeout=5):
            ark_window.tap('expedite_confirm')
            ark_window.wait_gone('expedite_confirm', timeout=3)
        
    def do_recruitment(self):
        """Perform a full recruitment cycle."""
        logger.info("Starting daily recruitment scenario...")
        for i in range(1, 5):
            logger.debug(f"Recruitment cycle for tile {i}")
            self._click_recruitment_tile(i)
            self._confirm_recruitment(i)

    def do_daily_recruits(self, use_expedite: bool = None):
        if use_expedite is not None:
            self.use_expedite = use_expedite
        """Main method to execute the daily recruitment scenario based on chosen mode."""
        for i in range(1, 5):
            sleep(1)
            tile_status = self.check_tile(i)
            logger.info(f"Tile {i} status: {tile_status} in main loop")
            if tile_status == 'no_recruitment':
                self._click_recruitment_tile(i)
                
                if self.rare_option_available():
                    logger.info(f"Rare recruitment option available for tile {i}")
                    ark_window.tap('recruit_close_panel_button')
                    ark_window.wait_gone('recruitment_panel_indicator', timeout=5)
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
                    
                    if self.rare_option_available():
                        logger.info(f"Rare recruitment option available for tile {i}")
                        ark_window.tap('recruit_close_panel_button')
                        ark_window.wait_gone('recruitment_panel_indicator', timeout=5)
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
    def is_main_menu_visible(self):
        # Use consolidated multi-point check
        return ark_window.is_visible("main_menu_indicators")

    def return_to_main_menu(self, max_presses=6):
        """
        Press back until:
        - back_button disappears, and
        - main menu confirms appear.
        """
        for _ in range(max_presses):
            if self.is_main_menu_visible():
                return True
            # Either press keyboard back/esc or tap the on-screen back button if you prefer
            ark_window.click(*get_element('back_button').click_coords)
            ark_window.wait_gone("back_button", timeout=0.1)
            if ark_window.wait_visible("main_menu_indicators", timeout=0.25):
                return True
        # Final check
        return ark_window.wait_visible("main_menu_indicators", timeout=5.0)

    def navigate_to(self, tile_name: str, target_state: str, retries: int = 21, wait_visible_after_click: bool = True, post_click_timeout: float = 0.1):
        """
        Click a tile, confirm we arrived with target_state, retry after recovery if needed.
        """
        for attempt in range(retries + 1):
            
            ark_window.safe_click(get_element(tile_name).click_coords, expect_visible=None)
            
            if wait_visible_after_click:
                indicator_name = get_state_indicator_element_name(target_state)
                if indicator_name:
                    ark_window.wait_visible(indicator_name, timeout=post_click_timeout)
            
            if ark_window.wait_state(target_state, timeout=Settings.timeouts.default_timeout):
                return True
            
            # Didn't arrive; recover and retry
            self.return_to_main_menu()
        
        return False
class Base:
    """
    This class automates the base process in Arknights.
    """
    
    def _detect_notification_position(self):
        """
        Detect notification button position based on color check.
        Returns: 'upper', 'lower', or None if no notification present.
        """
        check_coords = get_element("notification_color_check").click_coords
        color = ark_window.get_pixel_color(*check_coords)
        red, green, blue = color
        
        logger.debug(f"Notification color check at {check_coords}: RGB={color}")
        
        # Check for emergency (red button): red < 190 and blue > 200 -> notification is upper
        if red < 190 and blue > 200:
            logger.info("Emergency detected, notification is in upper position")
            return 'upper'
        # Check for normal notification: red > 190 and blue < 190 -> notification is lower
        elif red > 190 and blue < 190:
            logger.info("Normal state, notification is in lower position") 
            return 'lower'
        else:
            logger.info("No notification button detected - dailies already completed")
            return None
    
    def open_notification(self):
        """Open the notification using smart position detection."""
        position = self._detect_notification_position()
        if position is None:
            logger.info("No notification to open - base dailies already completed")
            return False
            
        element_name = f"notification_{position}"
        coords = get_element(element_name).click_coords
        logger.debug(f"Opening notification at {position} position: {coords}")
        ark_window.click_and_wait(coords, coords, (255, 255, 255), mode='disappear', timeout=5)
        return True

    def close_notification(self):
        """Close the notification using smart position detection."""
        position = self._detect_notification_position()
        if position is None:
            logger.info("No notification to close")
            return False
            
        element_name = f"notification_{position}" 
        coords = get_element(element_name).click_coords
        logger.debug(f"Closing notification at {position} position: {coords}")
        ark_window.click_and_wait(coords, coords, (255, 255, 255), mode='appear', timeout=5)
        return True
    
    def click_notification_tiles(self):
        """Click the notification tiles."""
        click_coords = (270, 1000)
        
        for _ in range(8):
            ark_window.click(*click_coords)
            sleep(1)

class TaskAggregator:
	"""
	Aggregates and controls all daily automation tasks.
	"""
	
	def __init__(self, use_expedite=None, finish_on_recruitment=None, use_total_proxy=None, orundum_location=None,
				 store_based_on: list[str] = None,
				 store_rarity_priority: list[str] = None):
		# Fallback to Settings.arknights when not explicitly provided
		ak = Settings.arknights
		self.daily_recruits = DailyRecruits(
			use_expedite=ak.use_expedite if use_expedite is None else use_expedite,
			finish_on_recruitment=ak.finish_on_recruitment if finish_on_recruitment is None else finish_on_recruitment,
		)
		self.base = Base()
		self.main_menu = MainMenu()
		self.missions = Missions()
		self.friends = Friends()
		self.terminal = Terminal(
			amount_orundum=ak.amount_orundum,
			amount_sanity=ak.amount_sanity,
			orundum_income=ak.orundum_income,
			orundum_cap=ak.orundum_cap,
			sanity_taken=ak.sanity_taken,
			use_total_proxy=ak.use_total_proxy if use_total_proxy is None else use_total_proxy,
		)
		self.use_expedite = self.daily_recruits.use_expedite
		self.finish_on_recruitment = self.daily_recruits.finish_on_recruitment
		self.use_total_proxy = self.terminal.use_total_proxy
		self.orundum_location = ak.orundum_location if orundum_location is None else orundum_location
		self.store_based_on = list(ak.store_based_on) if store_based_on is None else store_based_on
		self.store_rarity_priority = list(ak.store_rarity_priority) if store_rarity_priority is None else store_rarity_priority
		logger.info("TaskAggregator initialized")
	
	def run_base_dailies(self):
		"""Execute base daily tasks."""
		logger.info("Starting base dailies...")
		# Navigate to base
		if not self.main_menu.navigate_to('tile_base', 'base_panel'):
			logger.error("Failed to navigate to base")
			return False
		
		# Execute base tasks
		sleep(7)
		# self.base.click_base_factory_tiles()
		# sleep(3)
		if self.base.open_notification():
			self.base.click_notification_tiles()
			self.base.close_notification()
			logger.info("Base dailies completed")
		else:
			logger.info("Base dailies already completed")
		
		# Return to main menu
		self.main_menu.return_to_main_menu()
		return True
	
	def run_recruitment_dailies(self):
		"""Execute recruitment daily tasks."""
		logger.info("Starting recruitment dailies...")
		# Navigate to recruitment
		if not self.main_menu.navigate_to('tile_recruit', 'recruitment_panel'):
			logger.error("Failed to navigate to recruitment")
			return False
		
		# Execute recruitment tasks
		self.daily_recruits.do_daily_recruits(use_expedite=self.use_expedite)
		self.daily_recruits.do_daily_recruits(use_expedite=False)
		logger.info("Recruitment dailies completed")
		
		# Return to main menu
		self.main_menu.return_to_main_menu()
		return True
	
	def run_missions_dailies(self):
		"""Execute missions daily tasks."""
		logger.info("Starting missions dailies...")
		# Navigate to missions
		if not self.main_menu.navigate_to('tile_missions', 'missions_panel'):
			logger.error("Failed to navigate to missions")
			return False
		sleep(1)
		# Execute missions tasks
		self.missions.collect_all_rewards()
		logger.info("Missions dailies completed")
		
		# Return to main menu
		self.main_menu.return_to_main_menu()
		return True
	
	def run_friends_dailies(self):
		"""Execute friends daily tasks."""
		logger.info("Starting friends dailies...")
		# Navigate to friends
		if not self.main_menu.navigate_to('tile_friends', 'friends_panel'):
			logger.error("Failed to navigate to friends")
			return False
		
		# Execute friends tasks
		self.friends.open_friends()
		self.friends.click_next_button()
		self.friends.exit_friends()
		logger.info("Friends dailies completed")
		
		# Return to main menu
		self.main_menu.return_to_main_menu()
		return True
	
	def run_terminal_dailies(self):
		"""Execute terminal daily tasks."""
		logger.info("Starting terminal dailies...")
		# Navigate to terminal
		if not self.main_menu.navigate_to('tile_terminal', 'terminal_panel', post_click_timeout=2):
			logger.error("Failed to navigate to terminal")
			return False
		# Execute terminal tasks
		self.terminal.open_orundum_switch()
		self.terminal.open_location(self.orundum_location)
		self.terminal.run_simulation(use_total_proxy=self.use_total_proxy)
		logger.info("Terminal dailies completed")
		
		# Return to main menu
		self.main_menu.return_to_main_menu()
		return True
	
	def run_all_dailies(self):
		"""Execute all daily tasks in sequence."""
		logger.info("Starting all daily tasks...")
		
		tasks = [
			("Recruitment", self.run_recruitment_dailies),
			("Base", self.run_base_dailies),
			("Friends", self.run_friends_dailies),
			("Store", self.run_store_tasks),
			("Missions", self.run_missions_dailies),
			("Terminal", self.run_terminal_dailies),
			("Missions", self.run_missions_dailies),
		]
		
		for task_name, task_func in tasks:
			try:
				logger.info(f"Executing {task_name} tasks...")
				success = task_func()
				if success:
					logger.info(f"{task_name} tasks completed successfully")
				else:
					logger.warning(f"{task_name} tasks failed")
			except Exception as e:
				logger.error(f"Error during {task_name} tasks: {e}")
				# Try to recover to main menu
				self.main_menu.return_to_main_menu()
		
		logger.info("All daily tasks completed")
		
	def run_store_tasks(self):
		"""Execute store tasks: navigate, claim, and buy according to priorities."""
		logger.info("Starting store dailies...")
		# Navigate to store
		if not self.main_menu.navigate_to('tile_store', STORE_PANEL):
			logger.error("Failed to navigate to store")
			return False
		self.store.open_credit_store()
		
		# Claim available freebies if present
		self.store.click_claim_button()
		
		# Buy tiles by priority (rarity then discount)
		result = self.store.buy_all_tiles(based_on=self.store_based_on, rarity_priority=self.store_rarity_priority)
		if result == 'insufficient_credit':
			logger.info("Stopping store tasks due to insufficient credit; returning to main menu")
			self.main_menu.return_to_main_menu()
			return True
		
		# Return to main menu
		self.main_menu.return_to_main_menu()
		logger.info("Store dailies completed")
		return True

class Missions:
    """
    This class automates the missions process in Arknights.
    """
    
    def __init__(self):
        pass
    
    def collect_daily_rewards(self):
        """Collect the daily rewards."""
        coords = get_element('mission_collect_all_button').click_coords
        color = get_element('mission_collect_all_button').pixel_points[0][2]
        for _ in range(3):
            ark_window.click_and_wait(coords, coords, color, mode='disappear', timeout=5)
        
    def collect_weekly_rewards(self):
        """Collect the weekly rewards."""
        weekly_coords = get_element('weekly_mission_button').click_coords
        weekly_color = get_element('weekly_mission_button').pixel_points[0][2]
        ark_window.click_and_wait(weekly_coords, weekly_coords, weekly_color, mode='disappear', timeout=5)
        
        collect_coords = get_element('mission_collect_all_button').click_coords
        collect_color = get_element('mission_collect_all_button').pixel_points[0][2]
        for _ in range(3):
            ark_window.click_and_wait(collect_coords, collect_coords, collect_color, mode='disappear', timeout=5)
        
    def collect_all_rewards(self):
        """Collect all rewards."""
        self.collect_daily_rewards()
        self.collect_weekly_rewards()

class Friends:
    """
    This class automates the friends process in Arknights.
    """
    
    def __init__(self):
        pass
    
    def open_friends(self):
        """Open the friends panel."""
        friend_menu_coords = get_element('friends_menu').click_coords
        friend_menu_color = get_element('friends_menu').pixel_points[0][2]
        ark_window.click_and_wait(friend_menu_coords, friend_menu_coords, friend_menu_color, mode='disappear', timeout=5)
        friend_tile_coords = get_element('friend_tile').click_coords
        sleep(2)
        ark_window.spam_click_until_color(friend_tile_coords, friend_menu_coords, (49, 49, 49), mode='disappear', timeout=15, click_delay=0.7)
        wait_coords = (1645, 68)
        wait_color = (111, 37, 0)
        ark_window.wait_for_color_change(wait_coords, wait_color, mode='appear', timeout=17)
    
    def click_next_button(self):
        """Click the next button."""
        next_button_coords = get_element('next_button').click_coords
        wait_color = get_element('next_button').pixel_points[0][2]
        wait_coords = (1645, 68)
        
        for _ in range(10):
            ark_window.click_and_wait(next_button_coords, wait_coords, wait_color, mode='disappear', timeout=5)
            sleep(0.5)
            ark_window.wait_for_color_change(wait_coords, wait_color, mode='appear', timeout=15)
       
    def exit_friends(self):
        """Exit the friends panel."""
        ark_window.safe_click(get_element('back_button').click_coords, expect_visible=None)
        confirm_coords = get_element('confirm_button').click_coords
        confirm_color = get_element('confirm_button').pixel_points[0][2]
        ark_window.wait_for_color_change(confirm_coords, confirm_color, mode='appear', timeout=5)
        ark_window.click_and_wait(confirm_coords, confirm_coords, confirm_color, mode='disappear', timeout=5)
        
        friend_menu_coords = get_element('friends_menu').click_coords
        friend_menu_color = get_element('friends_menu').pixel_points[0][2]
        ark_window.wait_for_color_change(friend_menu_coords, friend_menu_color, mode='appear', timeout=20)

class Terminal:
    """
    This class automates the terminal process in Arknights.
    """
    
    def __init__(self, amount_orundum: int = 0, amount_sanity: int = 174, orundum_income: int = 330, orundum_cap: int = 1800, sanity_taken: int = 25, use_total_proxy: bool = False):
        self.amount_orundum = amount_orundum
        self.amount_sanity = amount_sanity
        self.orundum_income = orundum_income
        self.orundum_cap = orundum_cap
        self.sanity_taken = sanity_taken
        self.use_total_proxy = use_total_proxy
        
    def open_orundum_switch(self):
        """Open the orundum farming panel."""
        orundum_menu_coords = get_element('orundum_menu_button').click_coords
        orundum_menu_color = get_element('orundum_menu_button').pixel_points[0][2]
        
        ark_window.click_and_wait(orundum_menu_coords, orundum_menu_coords, orundum_menu_color, mode='disappear', timeout=5)
        
        back_button_coords = get_element('back_button').click_coords
        sleep(0.5)
        ark_window.click(*back_button_coords)
        sleep(1)
        orundum_switch_coords = get_element('orundum_location_switch_button').click_coords
        wait_coords = get_element('orundum_current_mission').click_coords
        wait_color = get_element('orundum_current_mission').pixel_points[0][2]
        ark_window.click_and_wait(orundum_switch_coords, wait_coords, wait_color, mode='appear', timeout=5)
        
    def open_location(self, location: str|int):
        """Open the orundum farming panel."""
        if isinstance(location, int):
            location = f"orundum_permanent_mission_{location}"
        elif get_element(location).pixel_points is None:
            logger.warning(f"Location {location} is not a valid location. Defaulting to permanent mission 1")
            location = f"orundum_permanent_mission_1"
        
        location_coords = get_element(location).click_coords
        location_color = get_element(location).pixel_points[0][2]
        
        ark_window.click_and_wait(location_coords, location_coords, location_color, mode='disappear', timeout=5)
            
        start_button_coords = get_element('start_button').click_coords
        start_button_color = get_element('start_button').pixel_points[0][2]
        ark_window.wait_for_color_change(start_button_coords, start_button_color, mode='appear', timeout=10)
        
    def _is_auto_deploy_on(self):
        """Check if the auto deploy is on."""
        auto_deploy_coords = get_element('auto_deploy_button').click_coords
        auto_deploy_color = get_element('auto_deploy_button').pixel_points[0][2]
        return ark_window.check_color_at(*auto_deploy_coords, auto_deploy_color, confidence=1)
        
    def _is_total_proxy_available(self):
        """Check if the total proxy is available."""
        total_proxy_coords = get_element('total_proxy_available').click_coords
        total_proxy_color = get_element('total_proxy_available').pixel_points[0][2]
        
        if self._is_auto_deploy_on():
            auto_deploy_coords = get_element('auto_deploy_button').click_coords
            auto_deploy_color = get_element('auto_deploy_button').pixel_points[0][2]
            ark_window.click_and_wait(auto_deploy_coords, auto_deploy_coords, auto_deploy_color, mode='disappear', timeout=5)
            proxy_available = ark_window.check_color_at(*total_proxy_coords, total_proxy_color, confidence=0.8)
            ark_window.click_and_wait(auto_deploy_coords, auto_deploy_coords, auto_deploy_color, mode='appear', timeout=5)
            logger.info(f"Total proxy available: {proxy_available}")
            return proxy_available
        
        proxy_available = ark_window.check_color_at(*total_proxy_coords, total_proxy_color, confidence=0.8)
        logger.info(f"Total proxy available: {proxy_available}")
        self.total_proxy_available = bool(proxy_available)
        
        return proxy_available
        
    def run_simulation(self, use_total_proxy: bool = None):
        """Run the simulation."""
        if use_total_proxy is not None:
            self.use_total_proxy = use_total_proxy
        # sleep(1)
        self.total_proxy_available = bool(self._is_total_proxy_available())
        # sleep(1)
        total_proxy_used = False
        if self.use_total_proxy:
            if self.total_proxy_available:
                logger.info("Total proxy is available, using total proxy")
                total_proxy_coords = get_element('total_proxy_available').click_coords
                total_proxy_color = get_element('total_proxy_available').pixel_points[0][2]
                ark_window.click_and_wait(total_proxy_coords, total_proxy_coords, total_proxy_color, mode='disappear', timeout=5)
                final_timeout = 15
                total_proxy_used = True
            else:
                logger.info("Total proxy is not available, deploying without it")
        else:
            logger.info("Total proxy is not used")
        
        sleep(0.5)
        if not self._is_auto_deploy_on():
            logger.info("Auto deploy is off, turning it on")
            auto_deploy_coords = get_element('auto_deploy_button').click_coords
            auto_deploy_color = get_element('auto_deploy_button').pixel_points[0][2]
            if ark_window.click_and_wait(auto_deploy_coords, auto_deploy_coords, auto_deploy_color, mode='appear', timeout=5):
                logger.info("Auto deploy is on")
            else:
                logger.info("Auto deploy is already on")
        else:
            logger.info("Auto deploy is on")
        
        start_button_coords = get_element('start_button').click_coords
        start_button_color = get_element('start_button').pixel_points[0][2]
        ok = ark_window.click_and_wait(start_button_coords, start_button_coords, start_button_color, mode='disappear', timeout=5)
        if not ok:
            logger.info('Maximum orundum reached, returning')
            return 'maximum_orundum_reached'
        
        mission_start_button_coords = get_element('mission_start_button').click_coords
        mission_start_button_color = get_element('mission_start_button').pixel_points[0][2]
        ark_window.click_and_wait(mission_start_button_coords, mission_start_button_coords, mission_start_button_color, mode='disappear', timeout=5)
        
        # Wait for mission_complete_screen element (verifies all 3 confirmation points)
        if not total_proxy_used:
            final_timeout = 2400
            sleep(15)
        else:
            final_timeout = 10
        if total_proxy_used:
            if ark_window.wait_visible('mission_complete_screen', timeout=final_timeout):
                logger.info("Mission complete screen appeared")
            else:
                logger.info("Mission complete screen did not appear")
        else:
            if ark_window.wait_visible('mission_non_proxy_complete_screen', timeout=final_timeout):
                logger.info("Mission complete screen appeared")
            else:
                logger.info("Mission complete screen did not appear")
        # Click the mission_complete_screen and wait until it disappears (all points gone)
        if total_proxy_used:
            ark_window.tap('mission_complete_screen')
            ark_window.tap('mission_complete_screen')
        else:
            ark_window.tap('mission_non_proxy_complete_screen')
            ark_window.tap('mission_non_proxy_complete_screen')
        
        mission_complete_el = get_element('mission_complete_screen')
        mission_complete_coords = mission_complete_el.click_coords
        # Use the color that corresponds to the exact wait coordinate (fallback to first anchor)
        mc_color = None
        if mission_complete_el.pixel_points:
            for px, py, rgb in mission_complete_el.pixel_points:
                if (px, py) == mission_complete_coords:
                    mc_color = rgb
                    break
        if mc_color is None:
            mc_color = mission_complete_el.pixel_points[0][2]
        ark_window.spam_click_until_color(mission_complete_coords, mission_complete_coords, mc_color, mode='disappear', timeout=15)
        return True
        
    def run_multiple_simulations(self, use_total_proxy: bool = False, amount_orundum: int = None, total_proxy_available: bool = None, amount_sanity: int = None):
        """Run multiple simulations."""
        if amount_orundum is None:
            amount_orundum = self.amount_orundum
        if total_proxy_available is None:
            total_proxy_available = self.total_proxy_available
        if amount_sanity is None:
            amount_sanity = self.amount_sanity
        from math import ceil
        simulations_needed = ceil((self.orundum_cap - self.amount_orundum) / self.orundum_income)
        sanity_needed = simulations_needed * self.sanity_taken
        
        if amount_sanity < self.sanity_taken:
            logger.warning(f"Not enough sanity to run a single simulation. Need {sanity_needed} sanity.")
            return False
        
        if amount_sanity < sanity_needed:
            simulations_possible = amount_sanity // self.sanity_taken
            logger.warning(f"Not enough sanity to run {simulations_needed} simulations. Need {sanity_needed} sanity. Running {simulations_possible} simulations.")
            simulations_needed = simulations_possible
        
        logger.info(f"Running {simulations_needed} simulations")
        
        for i in range(simulations_needed):
            logger.info(f"Running simulation {i + 1} of {simulations_needed}...")
            status = self.run_simulation(use_total_proxy=use_total_proxy)
            if status == 'maximum_orundum_reached':
                logger.info('Maximum orundum reached, returning')
                return True 
            self.amount_orundum += self.orundum_income
            self.amount_sanity -= self.sanity_taken
        
        logger.info(f"Orundum gained: {self.amount_orundum}, Sanity: ~{self.amount_sanity}")
        return True

class Store:
    """
    Store screen helpers.
    """
    TILE_W = 355
    TILE_H = 355
    
    def open_credit_store(self):
        """
        Open the credit store.
        """
        ark_window.safe_click('credit_store_button', expect_visible='credit_store_interface_indicator_bottom')
        
    def _tile_info(self, tile_number: int):
        """
        Return a dict of dicts with key points for a given store tile.
        
        - tile_number: 1..10
        - Each entry contains base coords, and optional rgb placeholder.
        """
        if not (1 <= tile_number <= 10):
            raise ValueError("tile_number must be in 1..10")
        
        el_name = f"store_tile_{tile_number}"
        el = get_element(el_name)
        if not el or not el.click_coords:
            raise ValueError(f"Element '{el_name}' not defined or missing click_coords")
        
        x, y = el.click_coords  # top-left corner in base coordinates
        cx = x + self.TILE_W // 2
        cy = y + self.TILE_H // 2
        
        info = {
            "top_left": {
                "coords": (x, y),
                "rgb": None,
            },
            "center": {
                "coords": (cx, cy),
                "rgb": None,
            },
            "discount_position": {
                "coords": (x + 22, y + 63),
                "rgb": (93, 137, 0),
            },
            "available_position": {
                "coords": (x + 100, y + 10),
                "rgb": (49, 49, 49),
            },
            "circle_position_left": {
                "coords": (x + 81, y + 184),
                "rgb": None,
            },
            "circle_position_right": {
                "coords": (x + 260, y + 186),
                "rgb": None,
            },
            "circle_position_upper": {
                "coords": (x + 161, y + 94),
                "rgb": None,
            },
            "circle_position_lower": {
                "coords": (x + 188, y + 272),
                "rgb": None,
            },
            
            
        }
        return info
        
    def _has_discount(self, tile_number: int):
        """
        Check if the tile has a discount.
        """
        discount_position = self._tile_info(tile_number)["discount_position"]["coords"]
        discount_rgb = self._tile_info(tile_number)["discount_position"]["rgb"]
        return ark_window.check_color_at(*discount_position, discount_rgb, confidence=1)
        
    def is_available(self, tile_number: int):
        """
        Check if the tile is sold out.
        """
        available_position = self._tile_info(tile_number)["available_position"]["coords"]
        available_rgb = self._tile_info(tile_number)["available_position"]["rgb"]
        return ark_window.check_color_at(*available_position, available_rgb, confidence=1)
        
    def determine_rarity(self, tile_number: int):
        """
        Determine the rarity of the tile.
        """
        import math
        info = self._tile_info(tile_number)
        sample_points = [
            info["circle_position_left"]["coords"],
            info["circle_position_right"]["coords"],
            info["circle_position_upper"]["coords"],
            info["circle_position_lower"]["coords"],
        ]
        
        # Rarity palette (BGR noted by user visuals, but we use RGB tuples here)
        palette = {
            "common_gray": (162, 162, 162),
            "uncommon_yellow": (220, 229, 53),
            "rare_blue": (0, 177, 255),
            "very_rare_pink": (215, 198, 213),
            "extremely_rare_orange": (255, 200, 0),
        }
        
        def similarity(a, b):
            dr = a[0] - b[0]
            dg = a[1] - b[1]
            db = a[2] - b[2]
            dist = math.sqrt(dr * dr + dg * dg + db * db)
            max_dist = math.sqrt(3 * 255 * 255)
            return max(0.0, 1.0 - dist / max_dist)
        
        # Fetch colors at sample points
        found = [ark_window.get_pixel_color(x, y) for (x, y) in sample_points]
        
        # Score palette by MAX similarity over samples (robust to outliers/occlusions)
        best_rarity = "unknown"
        best_sim = -1.0
        for rarity, target in palette.items():
            max_sim = 0.0
            for c in found:
                s = similarity(c, target)
                if s > max_sim:
                    max_sim = s
            if max_sim > best_sim:
                best_sim = max_sim
                best_rarity = rarity
        
        # Require strong evidence from at least one point
        return best_rarity if best_sim >= 0.95 else "unknown"
        
    def determine_rarities(self):
        """
        Determine rarities for all 10 tiles.
        Returns a dict {tile_number: rarity}
        """
        results = {}
        for i in range(1, 11):
            try:
                results[i] = self.determine_rarity(i)
            except Exception as e:
                logger.info('Error determining rarity for tile %s', i, e)
                results[i] = "unknown"
        return results
        
    def click_claim_button(self):
        """
        Click the claim button.
        """
        claim_button_coords = get_element('claim_button').click_coords
        claim_button_color = get_element('claim_button').pixel_points[0][2]
        if ark_window.check_color_at(*claim_button_coords, claim_button_color, confidence=1):
            logger.info("Claim button is available, clicking it")
            ark_window.click_and_wait(claim_button_coords, claim_button_coords, claim_button_color, mode='disappear', timeout=5)
            
            credit_store_indicator_coords = get_element('credit_store_interface_indicator_bottom').click_coords
            credit_store_indicator_color = get_element('credit_store_interface_indicator_bottom').pixel_points[0][2]
            ark_window.spam_click_until_color(credit_store_indicator_coords, credit_store_indicator_coords, credit_store_indicator_color, mode='appear', timeout=5)
        else:
            logger.info("Claim button is not available")
        
    def buy_tile(self, tile_number: int):
        """
        Buy the tile.
        """
        info = self._tile_info(tile_number)
        if not self.is_available(tile_number):
            logger.info("Tile is not available")
            return False
        tile_coords_available = info["available_position"]["coords"]
        buy_button_wait_coords = get_element('buy_button_credit_store').pixel_points[0][:2]
        buy_button_color = get_element('buy_button_credit_store').pixel_points[0][2]
        ark_window.click_and_wait(tile_coords_available, buy_button_wait_coords, buy_button_color, mode='appear', timeout=5)
        
        buy_button_coords = get_element('buy_button_credit_store').click_coords
        ok = ark_window.click_and_wait(buy_button_coords, buy_button_wait_coords, buy_button_color, mode='disappear', timeout=5)
        
        if not ok:
            logger.info("Insufficient credit, returning insufficient_credit")
            return 'insufficient_credit'
        
        logger.info(f"Bought tile {tile_number}")
        sleep(0.25)
        
        credit_store_indicator_coords = get_element('credit_store_interface_indicator_bottom').click_coords
        credit_store_indicator_wait_coords = get_element('credit_store_interface_indicator_bottom').pixel_points[0][:2]
        credit_store_indicator_color = get_element('credit_store_interface_indicator_bottom').pixel_points[0][2]
        ark_window.spam_click_until_color(credit_store_indicator_coords, credit_store_indicator_wait_coords, credit_store_indicator_color, mode='appear', timeout=5)
        # ark_window.wait_visible('credit_store_interface_indicator_bottom', timeout=5)
        
        return True
        
    #TODO: Implement "item" determination and add it to buy_all_tiles
    def buy_all_tiles(self, based_on: list[str] = ['rarity', 'discount'], rarity_priority: list[str] = ['extremely_rare_orange', 'very_rare_pink', 'rare_blue', 'uncommon_yellow', 'common_gray']):
        """
        Buy all tiles based on characteristics.
        based_on can take in these strings: "rarity", "discount", "item"
        Importance is determined by the order of the list.
        Also, the rarity priority is determined by the order of the list.
        The default rarity priority is extremely_rare_orange, very_rare_pink, rare_blue, uncommon_yellow, common_gray.
        """
        # Prepare ranking for rarities (lower rank => buy earlier)
        rarity_rank = {name: idx for idx, name in enumerate(rarity_priority)}
        unknown_rank = len(rarity_priority) + 1
        
        # Determine rarities for all tiles once
        rarities = self.determine_rarities()
        
        # Consider only tiles that are available
        candidates = [i for i in range(1, 11) if self.is_available(i)]
        
        def sort_key(tile_index: int):
            parts = []
            for criterion in based_on:
                if criterion == 'rarity':
                    r = rarities.get(tile_index, 'unknown')
                    parts.append(rarity_rank.get(r, unknown_rank))
                elif criterion == 'discount':
                    # True (has discount) should be bought earlier → use 0 for True, 1 for False
                    has_disc = self._has_discount(tile_index)
                    parts.append(0 if has_disc else 1)
                elif criterion == 'item':
                    # Not implemented yet; ignore
                    continue
            # Final tie-breaker: lower tile index first
            parts.append(tile_index)
            return tuple(parts)
        
        # Sort according to based_on priorities and buy in that order
        sorted_tiles = sorted(candidates, key=sort_key)
        
        bought = []
        for idx in sorted_tiles:
            status = self.buy_tile(idx)
            if status == 'insufficient_credit':
                logger.info("Insufficient credit detected during purchase; stopping further store buys")
                return 'insufficient_credit'
            elif not status:
                logger.info("Tile is not available")
            else:
                bought.append(idx)
            
        logger.info(f"Bought tiles: {bought}")
        return bought
        
if __name__ == "__main__":
	main_menu = MainMenu()
	base = Base()
	daily_recruits = DailyRecruits(use_expedite=False)
	task_aggregator = TaskAggregator(use_expedite=False, use_total_proxy=True)
	missions = Missions()
	friends = Friends()
	terminal = Terminal()
	store = Store()
	
	task_aggregator.run_all_dailies()