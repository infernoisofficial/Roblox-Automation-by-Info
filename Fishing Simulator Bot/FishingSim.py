import time
import keyboard
import numpy as np
import pyautogui
from PIL import ImageGrab

# --- CONFIGURATION & PERFORMANCE TUNING ---
pyautogui.PAUSE = 0  # Removes the default PyAutoGUI delay to maximize click speed
pyautogui.FAILSAFE = True  # Move mouse to any corner of the screen to abort script

# --- REFERENCES SECTION ---
# Colors (R, G, B)
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
GREY_COLOR = (188, 188, 188)
GREEN_COLOR = (83, 250, 83)
RED_COLOR = (251, 98, 76)

# Regions (left, top, right, bottom)
REGION_A = (100, 100, 1750, 950)
REGION_B = (1080, 798, 1171, 892)

# Specific Coordinate Points (x, y)
PT_GH = (1193, 766)
PT_EF = (1208, 757)
PT_IJ = (1002, 820)  # rest_location

# Conditions & Intervals
TIMER_CONDITION = 0.25  # 250 milliseconds
AUTOCLICK_INTERVAL = 0.15  # 50 milliseconds
MARGIN_COUNT = 100  # Pixel threshold

# Global States
fishing = False
state = "THROW"  # Internal states: THROW, WAIT_BITE, REELING, REELING_PAUSE

# --- HELPER FUNCTIONS ---


def toggle_fishing():
    global fishing, state
    fishing = not fishing
    if fishing:
        state = "THROW"
        print("[SYSTEM] Fishing Started (State: True)")
    else:
        print("[SYSTEM] Fishing Stopped (State: False)")


def count_pixels(img, target_color):
    """Counts exact matching color pixels using NumPy for extreme speed."""
    arr = np.array(img)
    mask = np.all(arr == target_color, axis=-1)
    return np.sum(mask)


def color_exists(img, target_color):
    """Checks if at least one pixel matches the target color."""
    arr = np.array(img)
    return np.any(np.all(arr == target_color, axis=-1))


# Register Hotkey Toggle (Press 'Q' to turn on/off)
keyboard.add_hotkey("q", toggle_fishing)

print("==============================================")
print("  FISHING BOT READY. Press 'Q' to Toggle ON/OFF  ")
print("==============================================")

# Timing variables
last_click_time = 0
last_timer_check = 0

# Baseline trackers for Region B
baseline_red = 0
baseline_white = 0

# --- MAIN LOOP ---
while True:
    # If fishing is toggled off, idle without consuming CPU
    if not fishing:
        time.sleep(0.1)
        continue

    current_time = time.time()

    # STEP 1: Throw Hook
    if state == "THROW":
        print("Throwing hook...")
        pyautogui.click()
        time.sleep(1.0)  # Short pause to allow hook throwing animation to begin
        state = "WAIT_BITE"

    # STEP 2: Wait for Bite (Region A)
    elif state == "WAIT_BITE":
        img_a = ImageGrab.grab(bbox=REGION_A)
        if color_exists(img_a, CYAN_COLOR):
            print("Bite detected! Hooking fish...")
            pyautogui.click()

            # Initialize Reeling Phase Reference Points
            img_b = ImageGrab.grab(bbox=REGION_B)
            baseline_red = count_pixels(img_b, RED_COLOR)
            baseline_white = count_pixels(img_b, WHITE_COLOR)

            last_click_time = current_time
            last_timer_check = current_time
            state = "REELING"

    # STEP 4: Reeling Phase (Auto-clicking running)
    elif state == "REELING":
        # Auto-clicking handling (Every 50ms)
        if current_time - last_click_time >= AUTOCLICK_INTERVAL:
            pyautogui.click()
            last_click_time = current_time

        # Condition (i): Timer condition check (Every 250ms)
        if current_time - last_timer_check >= TIMER_CONDITION:
            last_timer_check = current_time

            if pyautogui.pixelMatchesColor(PT_GH[0], PT_GH[1], GREY_COLOR):
                print("Scope of green is available")

                # Step 5: Check if Fish is caught
                if pyautogui.pixelMatchesColor(PT_EF[0], PT_EF[1], GREEN_COLOR):
                    print("Fish caught! Resetting loop...")
                    state = "THROW"  # Loop back to Step 1
                    time.sleep(1.5)  # Wait for catch animation before casting again
                    continue

        # Condition (ii): Region B pixel tracking
        img_b = ImageGrab.grab(bbox=REGION_B)
        current_red = count_pixels(img_b, RED_COLOR)
        current_white = count_pixels(img_b, WHITE_COLOR)

        decrease_red = baseline_red - current_red
        increase_white = current_white - baseline_white

        if decrease_red >= MARGIN_COUNT and increase_white >= MARGIN_COUNT:
            print("Reeling pause triggered. Clearing references.")
            state = "REELING_PAUSE"

    # STEP 6: Reeling Pause Phase (Auto-clicking stopped)
    elif state == "REELING_PAUSE":
        # Monitor rest location point (i, j) for white color change
        if pyautogui.pixelMatchesColor(PT_IJ[0], PT_IJ[1], WHITE_COLOR):
            print("Resuming Reeling. Re-establishing baseline references.")

            # Re-establish clean reference baselines for Region B upon exit
            img_b = ImageGrab.grab(bbox=REGION_B)
            baseline_red = count_pixels(img_b, RED_COLOR)
            baseline_white = count_pixels(img_b, WHITE_COLOR)

            last_click_time = current_time
            last_timer_check = current_time
            state = "REELING"

    # Small micro-sleep to prevent the script from thrashing a single CPU core thread
    time.sleep(0.001)