import pyautogui
import time
import os

def check_for_pixels():
    """
    Continuously checks the screen for specific pixel colors every 5 seconds.
    """
    # Target color to search for anywhere on screen
    target_color = (235, 220, 38)  # RGB color for both operators
    
    print("Starting pixel check...")
    print("Press Ctrl+C to stop the test.")
    print("Searching for operators anywhere on screen...")

    try:
        while True:
            found_operators = []
            
            # Get screen size
            screen_width, screen_height = pyautogui.size()
            
            # Search for the target color across the screen
            # Using a step size for performance - adjust as needed
            step_size = 10
            
            for x in range(0, screen_width, step_size):
                for y in range(0, screen_height, step_size):
                    try:
                        current_pixel = pyautogui.pixel(x, y)
                        
                        # Check if the current pixel matches the target color
                        if color_match(current_pixel, target_color, tolerance=15):
                            found_operators.append((x, y))
                            # Break after finding first match to avoid too many results
                            break
                    except Exception as e:
                        continue
                if found_operators:
                    break
            
            if found_operators:
                for pos in found_operators:
                    print(f"Operator detected at position {pos}")
            else:
                print("No operators detected on the screen.")

            # Wait for 2 seconds before the next check
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nPixel check stopped by user.")
    except Exception as e:
        print(f"An error stopped the script: {e}")

def color_match(color1, color2, tolerance=10):
    """
    Check if two RGB colors match within a given tolerance.
    
    Args:
        color1 (tuple): First RGB color (r, g, b)
        color2 (tuple): Second RGB color (r, g, b) 
        tolerance (int): Maximum difference allowed for each color component
        
    Returns:
        bool: True if colors match within tolerance, False otherwise
    """
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

if __name__ == '__main__':
    # Helper function to get pixel coordinates and colors
    print("To get pixel coordinates and colors:")
    print("1. Run: python -c \"import pyautogui; print('Position:', pyautogui.position())\" while hovering over target")
    print("2. Run: python -c \"import pyautogui; print('Color:', pyautogui.pixel(x, y))\" with your coordinates")
    print()
    
    check_for_pixels()
