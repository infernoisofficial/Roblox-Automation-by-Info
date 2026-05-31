import time
import pyautogui
import keyboard
import numpy as np
from PIL import ImageGrab

# ==========================================
#               REFERENCES
# ==========================================
# Colors (RGB format)
CYAN_COLOR  = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
GREY_COLOR  = (188, 188, 188)
GREEN_COLOR = (83, 250, 83)
RED_COLOR   = (251, 98, 76)

# Coordinate Boundaries: (x1, y1, x2, y2)
# Region A: (100,100) to (1750,950)
REG_A = (100, 100, 1750, 950)
# Region B: (1080,798) to (1171,892)
REG_B = (1080, 798, 1171, 892)

# Specific Pixel Points: (x, y)
PT_GH = (1193, 766)
PT_EF = (1208, 757)
PT_IJ = (1002, 820)  # rest_location

# Configuration Conditions
MARGIN_COUNT = 100
CLICK_INTERVAL = 0.25  # 250 milliseconds

# State Management Variables
fishing = False
state = "THROW_HOOK"  # Internal states: THROW_HOOK, WAIT_FOR_HOOK, REELING, REELING_PAUSE

# Tracking variables for performance & logic
last_click_time = 0
prev_red_count = 0
prev_white_count = 0
q_pressed = False

print(">>> Script Active. Press 'Q' to toggle Fishing ON/OFF. <<<")

# ==========================================
#          CORE STATE ENGINE
# ==========================================
while True:
    # Handle Toggle Key Q (with basic software debounce)
    if keyboard.is_pressed('q'):
        if not q_pressed:
            fishing = not fishing
            q_pressed = True
            print(f"\n--- Fishing State Changed: {'ENABLED' if fishing else 'DISABLED'} ---")
            if fishing:
                state = "THROW_HOOK"  # Always start fresh at Step 1
            time.sleep(0.3)
    else:
        q_pressed = False

    # If fishing is toggled off, pause script execution slightly to save CPU
    if not fishing:
        time.sleep(0.1)
        continue

    # --- STEP 1: Throw Hook ---
    if state == "THROW_HOOK":
        print("[Step 1] Throwing hook...")
        pyautogui.click()
        state = "WAIT_FOR_HOOK"
        time.sleep(1.0)  # Safe buffer delay to let the hook animation deploy

    # --- STEP 2: Wait for Hooked Signal ---
    elif state == "WAIT_FOR_HOOK":
        # Fast full-screen grab converted to numpy array
        img = np.array(ImageGrab.grab())
        
        # Crop array to Region A (Note: NumPy arrays use [y, x] formatting)
        reg_a = img[REG_A[1]:REG_A[3]+1, REG_A[0]:REG_A[2]+1]
        
        # Look for Cyan pixel matching (100% confidence match)
        cyan_mask = (reg_a[:, :, 0] == CYAN_COLOR[0]) & \
                    (reg_a[:, :, 1] == CYAN_COLOR[1]) & \
                    (reg_a[:, :, 2] == CYAN_COLOR[2])
        
        if np.any(cyan_mask):
            print("[Step 2] Cyan bubbles detected! Striking...")
            pyautogui.click()
            
            # Transition directly to Reeling (Step 4)
            state = "REELING"
            last_click_time = time.time()
            
            # Initialize baseline counts for Region B
            reg_b = img[REG_B[1]:REG_B[3]+1, REG_B[0]:REG_B[2]+1]
            prev_red_count = np.sum((reg_b[:, :, 0] == RED_COLOR[0]) & (reg_b[:, :, 1] == RED_COLOR[1]) & (reg_b[:, :, 2] == RED_COLOR[2]))
            prev_white_count = np.sum((reg_b[:, :, 0] == WHITE_COLOR[0]) & (reg_b[:, :, 1] == WHITE_COLOR[1]) & (reg_b[:, :, 2] == WHITE_COLOR[2]))

    # --- STEP 4: Reeling Phase ---
    elif state == "REELING":
        current_time = time.time()
        
        # Perform Auto-clicking every 250ms
        if current_time - last_click_time >= CLICK_INTERVAL:
            pyautogui.click()
            last_click_time = current_time
            
        img = np.array(ImageGrab.grab())
        
        # Check point (g,h) for Grey color
        if tuple(img[PT_GH[1], PT_GH[0]][:3]) == GREY_COLOR:
            print("scope of green is available")
            
        # Condition (i): Fish Caught check at point (e,f)
        if tuple(img[PT_EF[1], PT_EF[0]][:3]) == GREEN_COLOR:
            print("[Step 5] Fish Caught! Stopping auto-clicks.")
            state = "THROW_HOOK"  # Exit loop references, loop back to Step 1
            time.sleep(1.5)       # Buffer before repeating loop
            continue

        # Condition (ii): Check Region B for micro-changes
        reg_b = img[REG_B[1]:REG_B[3]+1, REG_B[0]:REG_B[2]+1]
        current_red_count = np.sum((reg_b[:, :, 0] == RED_COLOR[0]) & (reg_b[:, :, 1] == RED_COLOR[1]) & (reg_b[:, :, 2] == RED_COLOR[2]))
        current_white_count = np.sum((reg_b[:, :, 0] == WHITE_COLOR[0]) & (reg_b[:, :, 1] == WHITE_COLOR[1]) & (reg_b[:, :, 2] == WHITE_COLOR[2]))
        
        decrease_red = prev_red_count - current_red_count
        increase_white = current_white_count - prev_white_count
        
        # Check margins for Reeling Pause trigger
        if decrease_red >= MARGIN_COUNT and increase_white >= MARGIN_COUNT:
            print("[Step 6] Red dropped & White spiked. Entering Reeling Pause.")
            state = "REELING_PAUSE"
            
        # Update trackers for the next tick
        prev_red_count = current_red_count
        prev_white_count = current_white_count

    # --- STEP 6: Reeling Pause Phase ---
    elif state == "REELING_PAUSE":
        img = np.array(ImageGrab.grab())
        
        # Check if reference point (i,j) turns White
        if tuple(img[PT_IJ[1], PT_IJ[0]][:3]) == WHITE_COLOR:
            print("[Step 6] Rest point turned White. Resuming Reeling.")
            state = "REELING"
            last_click_time = time.time()  # Reset the click timer sequence
            
            # Reset baseline tracking numbers for Region B upon exit
            reg_b = img[REG_B[1]:REG_B[3]+1, REG_B[0]:REG_B[2]+1]
            prev_red_count = np.sum((reg_b[:, :, 0] == RED_COLOR[0]) & (reg_b[:, :, 1] == RED_COLOR[1]) & (reg_b[:, :, 2] == RED_COLOR[2]))
            prev_white_count = np.sum((reg_b[:, :, 0] == WHITE_COLOR[0]) & (reg_b[:, :, 1] == WHITE_COLOR[1]) & (reg_b[:, :, 2] == WHITE_COLOR[2]))

    # Millisecond frame sleep to prevent the processor thread from locking at 100% usage
    time.sleep(0.001)