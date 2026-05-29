import time
import keyboard
import pyautogui

# --- CONFIGURATION ---
# Replace these with your actual game coordinates
CHECK_X, CHECK_Y = 933, 820  # Step 3 coordinate
BREAK_X, BREAK_Y = 905, 350  # Step 4 coordinate

# Colors in RGB format
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)

# Color tolerance (0 means exact match, higher means more lenient)
TOLERANCE = 4

# Global state variable
fishing_enabled = False


def color_matches(c1, c2, tolerance=TOLERANCE):
    """Checks if two RGB colors are within a certain tolerance."""
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))


def scan_screen_for_color(target_color, tolerance=TOLERANCE):
    """Scans the screen to see if a color exists anywhere (used for the cyan bubbles).

    Note: Scanning the whole screen can be slow. If possible, restrict this
    to a specific region using pyautogui.screenshot(region=(x, y, w, h))
    """
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size

    # Optimizing by skipping pixels (checking every 5th pixel) for speed
    for x in range(0, width, 5):
        for y in range(0, height, 5):
            pixel_color = screenshot.getpixel((x, y))
            if color_matches(pixel_color, target_color, tolerance):
                return True
    return False


def toggle_fishing():
    """Toggles the fishing state when 'Q' is pressed."""
    global fishing_enabled
    fishing_enabled = not fishing_enabled
    print(f"\n[TOGGLE] Fishing enabled: {fishing_enabled}")
    time.sleep(0.3)  # Debounce delay


# Register the hotkey 'q' or 'Q'
keyboard.add_hotkey("q", toggle_fishing)

print("--- Fishing Script Started ---")
print("Press 'Q' to Pause/Resume fishing.")
print("Press 'Ctrl + C' in the terminal to exit completely.")
print("Starting in 3 seconds... Switch to your game window!")
time.sleep(3)


def main_fishing_loop():
    while True:
        # Extra Step 1 & 5: Check if fishing is enabled before throwing
        if not fishing_enabled:
            time.sleep(0.1)
            continue

        # Step 1: Click to throw the hook
        print("Throwing hook...")
        pyautogui.click()
        time.sleep(2)  # Wait a moment for the splash/hook to settle

        # Step 2: Wait and click if cyan bubbles appear
        print("Waiting for cyan bubbles...")
        bubbles_found = False
        while fishing_enabled and not bubbles_found:
            if scan_screen_for_color(CYAN_COLOR):
                print("Cyan detected! Pulling hook...")
                pyautogui.click()
                bubbles_found = True
            time.sleep(0.1)

        # Step 3 & 4: Minigame loop
        print("Entering reeling loop...")
        while fishing_enabled:
            # Step 4: Break loop if white at (a,b)
            pixel_break = pyautogui.pixel(BREAK_X, BREAK_Y)
            if color_matches(pixel_break, WHITE_COLOR):
                print("White detected at break coordinate. Fish caught!")
                break

            # Step 3: Click if white at (x,y)
            pixel_check = pyautogui.pixel(CHECK_X, CHECK_Y)
            if color_matches(pixel_check, WHITE_COLOR):
                print("White detected at check coordinate. Clicking...")
                pyautogui.click()

            time.sleep(0.05)  # Small delay to prevent CPU crashing

        time.sleep(1)  # Short pause before restarting the loop


if __name__ == "__main__":
    try:
        main_fishing_loop()
    except KeyboardInterrupt:
        print("\nScript stopped safely.")