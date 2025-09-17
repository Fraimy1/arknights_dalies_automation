import sys
from interface import run_console


def main():
    try:
        run_console()
    except KeyboardInterrupt:
        print("\nExiting PRTS console...")
        sys.exit(0)


if __name__ == "__main__":
    main()
