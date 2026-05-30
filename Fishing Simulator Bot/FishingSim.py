import time
import keyboard
import pyautogui

# --- Configuration & Coordinates ---
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
GREEN_COLOR = (83, 255, 83)  # Adjusted 259 to 255 max RGB

# Region A: (x, y, width, height)
# Left: 150, Top: 150, Width: 1710-150=1560, Height: 893-150=743
REGION_A = (150, 150, 1560, 743)

POINT_XY = (1031, 820)
POINT_UV = (941, 819)
POINT_EF = (729, 756)

# Performance Tuning
COLOR_CONFIDENCE = 15  # Tolerance allowance for slight RGB variations
LOOP_DELAY = 0.05  # Prevent 100% CPU usage

# --- State Variables ---
fishing_active = False
macro_running = True


def toggle_fishing():
    global fishing_active
    fishing_active = not fishing_active
    print(f"\n[TOGGLE] Fishing is now: {'ENABLED' if fishing_active else 'DISABLED'}")
    if fishing_active:
        print("[STATUS] Starting fresh cycle. Casting hook...")
        pyautogui.click()  # Step 1: Throw hook immediately on enable
        time.sleep(1)


# Register the 'Q' key to toggle the state instantly
keyboard.add_hotkey("q", toggle_fishing)

print("=== Fishing Bot Initialized ===")
print("Press 'Q' to Enable/Disable fishing.")
print("Hold 'Ctrl+C' in terminal to completely exit.")

try:
    while macro_running:
        if not fishing_active:
            time.sleep(0.2)  # Idle state wait
            continue

        # ----------------------------------------------------
        # Step 2: Look for Cyan bubbles in Region A
        # ----------------------------------------------------
        # Take a fast screenshot of just Region A
        screen_sample = pyautogui.screenshot(region=REGION_A)
        found_cyan = False

        # Scan the screenshot for the cyan color (stepping by 10 pixels for speed)
        for x in range(0, screen_sample.width, 10):
            for y in range(0, screen_sample.height, 10):
                r, g, b = screen_sample.getpixel((x, y))
                
                # Check if pixel color matches CYAN within confidence bounds
                if (abs(r - CYAN_COLOR[0]) <= COLOR_CONFIDENCE and 
                    abs(g - CYAN_COLOR[1]) <= COLOR_CONFIDENCE and 
                    abs(b - CYAN_COLOR[2]) <= COLOR_CONFIDENCE):
                    found_cyan = True
                    break
            if found_cyan:
                break

        if found_cyan:
            print("[Step 2] Cyan bubbles detected! Pulling the hook...")
            pyautogui.click()
            time.sleep(1.0)  # Wait briefly for reel UI to appear

            green_was_seen = False

            # ----------------------------------------------------
            # Step 3 & 4: Reeling Loop
            # ----------------------------------------------------
            print("[Step 3/4] Entering Reeling phase...")
            while fishing_active:
                
                # Check for Green appearance at (e,f)
                if pyautogui.pixelMatchesColor(POINT_EF[0], POINT_EF[1], GREEN_COLOR, tolerance=COLOR_CONFIDENCE):
                    if not green_was_seen:
                        print("[Step 5] Green color appeared at (e,f)!")
                        green_was_seen = True

                # Step 5: Fish Caught condition (Green color disappears after being seen)
                if green_was_seen:
                    if not pyautogui.pixelMatchesColor(POINT_EF[0], POINT_EF[1], GREEN_COLOR, tolerance=COLOR_CONFIDENCE):
                        print("[Step 5] Green color disappeared! Fish Caught!")
                        time.sleep(1.5)  # Wait for catch animation to finish
                        print("[Loop Reset] Casting hook for next fish...")
                        pyautogui.click()  # Step 1: Throw hook again
                        break  # Break reeling loop, returns to step 2 scanning

                # Check white color conditions for Reeling / Pausing
                white_at_xy = pyautogui.pixelMatchesColor(POINT_XY[0], POINT_XY[1], WHITE_COLOR, tolerance=COLOR_CONFIDENCE)
                white_at_uv = pyautogui.pixelMatchesColor(POINT_UV[0], POINT_UV[1], WHITE_COLOR, tolerance=COLOR_CONFIDENCE)

                if white_at_xy:
                    # White seen at (x,y) -> Pause reeling (do nothing/wait)
                    time.sleep(LOOP_DELAY)
                elif white_at_uv:
                    # White seen at (u,v) -> Resume reeling click
                    pyautogui.click()
                else:
                    # Default reeling behavior if neither condition overrides it
                    pyautogui.click()

                time.sleep(LOOP_DELAY)

        time.sleep(LOOP_DELAY)

except KeyboardInterrupt:
    print("\nBot stopped safely via terminal interrupt.")