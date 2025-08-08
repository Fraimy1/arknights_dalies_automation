import sys
from termcolor import colored
from scenarios import DailyRecruits

def main_menu():
    """
    Displays the main menu and handles user input.
    """
    while True:
        print(colored("========================================", "cyan"))
        print(colored("  Arknights Dailies Automation Tool  ", "white", "on_blue"))
        print(colored("========================================", "cyan"))
        print(colored("Please select a scenario to run:", "yellow"))
        print("1. Daily Recruits")
        print(colored("----------------------------------------", "cyan"))
        print("0. Quit")
        print(colored("========================================", "cyan"))

        choice = input("Enter your choice: ")

        if choice == '1':
            DailyRecruits().do_daily_recruits()
        elif choice == '0':
            print(colored("Exiting the application. Goodbye!", "green"))
            sys.exit()
        else:
            print(colored("Invalid choice, please try again.", "red"))
        
        input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user. Exiting...")
        sys.exit(0)
