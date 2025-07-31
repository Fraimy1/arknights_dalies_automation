from utils import ArknightsWindow
from time import sleep
import pyautogui as pg

ark_window = ArknightsWindow()
def do_daily_recruits():
    """
    This scenario automates the daily recruitment process in Arknights.
    """
    print("Starting daily recruitment scenario...")
    
    coords = {
            1: (486, 435),
            2: (1433, 435),
            3: (486, 851),
            4: (1433, 851),
        }
    
    def click_recruitment_tile(n: int):
        """Clicks the nth recruitment tile (1–4)."""
        screen_coords = ark_window.get_screen_coords(*coords[n])
        pg.click(*screen_coords)

    def confirm_recruitment(i):
        pg.click(*ark_window.get_screen_coords(674, 449)) # set time to 9
        pg.click(*ark_window.get_screen_coords(1463, 876)) # confirm recruitment
        
        for _ in range(10000): # waiting for the loading screen to finish
            check_coords = ark_window.get_scaled_coords(coords[i][0]-105, coords[i][1]+25)    
            if ark_window.check_color_at(*check_coords, (255, 255, 255), confidence=0.8):
                print(i, coords[i], check_coords)
                print("Recruitment confirmed.")
                break
            sleep(0.001)

    def do_recruitment():
        """Perform a full recruitment cycle."""
        for i in range(1, 5):
            click_recruitment_tile(i)
            confirm_recruitment(i)

    def click_hiring_tile(i):
        """Click the hiring tile to start the recruitment process."""
        screen_coords = ark_window.get_screen_coords(coords[i][0], coords[i][1]-136)
        pg.click(*screen_coords)
        
    def skip_button():
        """Click the skip button to skip the hiring animation."""
        screen_coords = ark_window.get_screen_coords(1833, 51)
        pg.click(*screen_coords)

    def do_hiring():
        """Perform the hiring process."""
        for i in range(1, 5):
            click_hiring_tile(i)
            confirm_recruitment(i)

    do_recruitment()

do_daily_recruits()