import time
import keyboard
import pyautogui
from PIL import ImageGrab, ImageOps
import pytesseract

# --- CONFIGURATION ---
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
COLOR_CONFIDENCE = 15  # Tolerance for color matching (0 to 255)

# Regions defined as (left, top, right, bottom)
REGION_G = (1017, 820, 1059, 830)
REGION_H = (707, 337, 1239, 369)

# Fast clicking interval (10 milliseconds = 0.010 seconds)
FAST_CLICK_INTERVAL = 0.010 

# State Variable
fishing = False

def colors_match(c1, c2, tolerance):
    """Checks if two colors are within a specific tolerance range."""
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def is_color_in_region(region, target_color, tolerance):
    """Scans a region to see if the target color exists within it."""
    screenshot = ImageGrab.grab(bbox=region)
    width, height = screenshot.size
    for x in range(width):
        for y in range(height):
            pixel = screenshot.getpixel((x, y))
            if colors_match(pixel, target_color, tolerance):
                return True
    return False

def check_for_text(region):
    """Uses OCR to check if any readable text appears in the region."""
    screenshot = ImageGrab.grab(bbox=region)
    # Convert to grayscale to improve OCR accuracy
    screenshot = ImageOps.grayscale(screenshot)
    text = pytesseract.image_to_string(screenshot).strip()
    return len(text) > 0

def toggle_fishing():
    """Toggles the fishing state when 'Q' is pressed."""
    global fishing
    fishing = not fishing
    print(f"\n[SYSTEM] Fishing state changed. Active: {fishing}")
    time.sleep(0.3) # Short delay to prevent accidental double-toggle

# Assign 'Q' key to toggle the bot on/off
keyboard.add_hotkey('q', toggle_fishing)

print("=== Fishing Bot Initialized ===")
print("Press 'Q' to START or STOP the bot.")
print("Press 'Ctrl + C' in the terminal to completely exit.")

# --- MAIN BOT LOOP ---
while True:
    if not fishing:
        time.sleep(0.1) # Idle sleep to save CPU when paused
        continue

    print("[STEP 1] Throwing the hook...")
    pyautogui.click()
    time.sleep(1) # Small delay to let the hook land

    # Step 2 & 6 Loop
    while fishing:
        # Look for cyan bubbles on the whole screen (or you can restrict this to a bbox for speed)
        # For performance, we grab a fullscreen shot to search for the cyan color
        screen = ImageGrab.grab()
        found_cyan = False
        
        # Quick sample scan for cyan (stepping pixels for speed)
        for x in range(0, screen.width, 5):
            for y in range(0, screen.height, 5):
                if colors_match(screen.getpixel((x, y)), CYAN_COLOR, COLOR_CONFIDENCE):
                    found_cyan = True
                    break
            if found_cyan:
                break

        if found_cyan:
            print("[STEP 2] Cyan bubbles detected! Pulling the hook...")
            pyautogui.click()
            time.sleep(0.1)

            print("[STEP 3] Entering fast-click loop...")
            while fishing:
                pyautogui.click()
                time.sleep(FAST_CLICK_INTERVAL)
                
                # Check if white color appears in Region G
                if is_color_in_region(REGION_G, WHITE_COLOR, COLOR_CONFIDENCE):
                    print("[STEP 3 SUCCESS] White color found in Region G. Breaking fast-click.")
                    break

            print("[STEP 4] Checking for text in Region H...")
            if check_for_text(REGION_H):
                print("[STEP 4] Text found in Region H! Breaking cycle.")
                break # Breaks out to step 5 (Throw hook again)
                
        time.sleep(0.05) # Prevent CPU frying while waiting for cyan bubbles