import time
import keyboard
import pyautogui
import numpy as np
from PIL import ImageGrab

# ==============================================================================
# REFERENCES & CONFIGURATION
# ==============================================================================
FISHING_ACTIVE = False  # Starting fishing state = false
REELING_STATE = None    # Reeling state = null

# Colors (Exact RGB matches for 100% confidence)
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
GREY_COLOR = (188, 188, 188)
GREEN_COLOR = (83, 250, 83)
RED_COLOR = (251, 98, 76)

# Coordinate Boundaries & Zones
# Region A bounding box: (left, top, right, bottom) calculated from (100,100) to (1750,950)
REGION_A_BBOX = (100, 100, 1750, 950)

RED_ZONE = [
    (1106, 843), (1113, 845), (1120, 848), (1127, 850), (1133, 853),
    (1140, 856), (1147, 858), (1153, 861), (1160, 865), (1167, 869)
]

GREEN_ZONE = [
    (1002, 820), (996, 819), (988, 819)
]

GH_POINT = (1193, 766)  # Reference point (g, h)
EF_POINT = (1208, 757)  # Reference point (e, f)

# Timers and Intervals
AUTO_CLICK_INTERVAL = 0.025  # 250 milliseconds

# ==============================================================================
# TOGGLE MECHANISM
# ==============================================================================
def toggle_fishing():
    global FISHING_ACTIVE, REELING_STATE
    FISHING_ACTIVE = not FISHING_ACTIVE
    if FISHING_ACTIVE:
        print("\n[SYSTEM] Fishing Started. Script is active.")
    else:
        print("\n[SYSTEM] Fishing Paused. Script is idle.")
        REELING_STATE = None
    time.sleep(0.4)  # Debounce delay

# Register 'Q' or 'q' as the global toggle hotkey
keyboard.add_hotkey('q', toggle_fishing)

print("====================================================")
print("  Python Auto-Fishing Script Initialized            ")
print("  Press 'Q' to Toggle Fishing ON / OFF              ")
print("====================================================")

# ==============================================================================
# MAIN CORE LOOP
# ==============================================================================
while True:
    # If fishing state is false, sleep lightly and keep checking
    if not FISHING_ACTIVE:
        time.sleep(0.1)
        continue

    # --------------------------------------------------------------------------
    # Step 1: Throw hook
    # --------------------------------------------------------------------------
    print("\nStep 1: Throwing hook -> Clicking screen.")
    pyautogui.click()
    time.sleep(1.0)  # Short pause to let the bobber/hook deploy cleanly

    # --------------------------------------------------------------------------
    # Step 2: Wait for bite (Cyan bubbles in Region A)
    # --------------------------------------------------------------------------
    print("Step 2: Monitoring Region A for cyan bubbles...")
    bite_detected = False
    
    while FISHING_ACTIVE and not bite_detected:
        # Fast memory grab of Region A
        region_img = ImageGrab.grab(bbox=REGION_A_BBOX)
        img_np = np.array(region_img)
        
        # Look for 100% exact match of CYAN_COLOR anywhere inside the matrix
        cyan_mask = (img_np[:, :, 0] == CYAN_COLOR[0]) & \
                    (img_np[:, :, 1] == CYAN_COLOR[1]) & \
                    (img_np[:, :, 2] == CYAN_COLOR[2])
                    
        if np.any(cyan_mask):
            print("Step 2: Change Detected! Cyan color pixels noticed.")
            bite_detected = True
        else:
            time.sleep(0.03)  # Tiny buffer to prevent CPU spikes

    if not FISHING_ACTIVE:
        continue

    # --------------------------------------------------------------------------
    # Step 3: Set a timer / Click to hook
    # --------------------------------------------------------------------------
    print("Step 3: Fish bit! Setting timer and clicking to initiate reel.")
    pyautogui.click()
    
    # Initialize Reeling state variables
    REELING_STATE = "Reeling"
    last_click_time = time.time()
    grey_msg_printed = False

    # --------------------------------------------------------------------------
    # Steps 4 & 6: Reeling Execution & Loop Switching
    # --------------------------------------------------------------------------
    while FISHING_ACTIVE and REELING_STATE != "Caught":
        
        # Take a single, swift full-screen grab for color matching accuracy across coordinates
        screen = ImageGrab.grab()
        
        if REELING_STATE == "Reeling":
            # --- Condition (i): Check if Fish is caught ---
            if screen.getpixel(EF_POINT) == GREEN_COLOR:
                print("Step 5: Fish caught! (Green detected at e,f reference). Exiting loops.")
                REELING_STATE = "Caught"
                break

            # --- Condition (ii): Check if Reeling Pause is triggered ---
            red_zone_triggered = False
            for pixel in RED_ZONE:
                if screen.getpixel(pixel) == WHITE_COLOR:
                    red_zone_triggered = True
                    break
            
            if red_zone_triggered:
                print("Step 4 -> Step 6: Reeling pause entered. Red zone pixel turned white.")
                REELING_STATE = "Pause"
                grey_msg_printed = False  # Reset grey check flags for the next cycle
                continue

            # --- Timer condition: Check (g,h) point for Grey Color ---
            if not grey_msg_printed:
                if screen.getpixel(GH_POINT) == GREY_COLOR:
                    print("Step 4: scope of green is available")
                    grey_msg_printed = True  # Ensures it prints only once per structural match

            # --- Auto-clicking Execution ---
            current_time = time.time()
            if current_time - last_click_time >= AUTO_CLICK_INTERVAL:
                pyautogui.click()
                last_click_time = current_time

        elif REELING_STATE == "Pause":
            # No auto-clicking happens here.
            # Safety check: Ensure we still monitor if the fish finishes catching during a pause
            if screen.getpixel(EF_POINT) == GREEN_COLOR:
                print("Step 5: Fish caught! (Green detected at e,f reference). Exiting loops.")
                REELING_STATE = "Caught"
                break
                
            # Wait until a change occurs: any one pixel in GREEN_ZONE turns white
            green_zone_triggered = False
            for pixel in GREEN_ZONE:
                if screen.getpixel(pixel) == WHITE_COLOR:
                    green_zone_triggered = True
                    break
            
            if green_zone_triggered:
                print("Step 6 -> Step 4: Reeling resumed. Green zone pixel turned white.")
                REELING_STATE = "Reeling"
                grey_msg_printed = False  # Reset checks for the coming reeling state
                last_click_time = time.time()  # Sync click timer to current time

        time.sleep(0.01)  # High performance yield statement

    # --------------------------------------------------------------------------
    # Step 7: Repeat sequence
    # --------------------------------------------------------------------------
    if REELING_STATE == "Caught":
        print("Step 7: Resetting configurations and looping back to Step 1.")
        REELING_STATE = None
        time.sleep(1.5)  # Wait for the UI animation to clear before restarting