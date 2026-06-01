import time
import pyautogui
import keyboard
import numpy as np
from PIL import ImageGrab

# ==========================================
# REFERENCES & CONFIGURATION
# ==========================================
# Colors (RGB)

#BUBBLE_COLOR = (68, 252, 234) #normal color
BUBBLE_COLOR = (253, 95, 10) #magma color (eruption island)
#BUBBLE_COLOR = (225, 109, 255) #purple neon color (eruption island)
WHITE_COLOR = (255, 255, 255)
GREY_COLOR = (188, 188, 188)
GREEN_COLOR = (83, 250, 83)
RED_COLOR = (251, 98, 76)

# Coordinate & Region Configurations
# Region A bounding box: (left, top, right, bottom)
REGION_A_BBOX = (100, 100, 1750, 950) 

# Reference points
GH_POINT = (1193, 766)
RED_ZONE = [(1083,835),(1092,838),(1099,840),(1106, 843), (1113, 845), (1120, 848), (1127, 850), (1133, 853), 
            (1140, 856), (1147, 858), (1153, 861), (1160, 865), (1167, 869)]
GREEN_ZONE = [(1020,822),(1012,821),(1004, 820), (996, 819), (988, 819)]

# Timer & Interval settings
TIMER_CONDITION = 0.25       # 0.25 seconds
CLICK_INTERVAL = 0.05        # 10 ms auto-clicking interval

# Bounding box for localized UI scanning (speeds up performance significantly)
# Encompasses GREEN_ZONE, RED_ZONE, and GH_POINT
UI_BBOX = (980, 750, 1210, 880)

# Initial States
fishing = False
scope_of_green = None

def toggle_fishing():
    global fishing
    fishing = not fishing
    if fishing:
        print("\n>>> [SYSTEM] Fishing Started. Active Mode. <<<")
    else:
        print("\n>>> [SYSTEM] Fishing Paused. Idle Mode. <<<")
    time.sleep(0.4) # Debounce to prevent accidental double-toggles

print("==================================================")
print(" Fishing Script Initialized.")
print(" Press 'Q' at any time to TOGGLE Fishing True/False.")
print("==================================================")

# ==========================================
# MAIN AUTOMATION LOOP
# ==========================================
while True:
    # Continuously monitor for toggle key
    if keyboard.is_pressed('q'):
        toggle_fishing()

    if not fishing:
        time.sleep(0.1)
        continue

    # --------------------------------------
    # STEP 1: Throw Hook
    # --------------------------------------
    print("1. Action: Throwing hook (Clicking).")
    pyautogui.click()
    time.sleep(1.0)  # Short delay for cast animation to stabilize

    # --------------------------------------
    # STEP 2: Wait for Bite (Cyan bubbles)
    # --------------------------------------
    print("2. Status: Waiting for cyan bubbles in Region A...")
    bite_detected = False
    
    while fishing:
        if keyboard.is_pressed('q'):
            toggle_fishing()
            break

        # Fast region scan using numpy
        screen_a = ImageGrab.grab(bbox=REGION_A_BBOX)
        img_np = np.array(screen_a)
        
        # Look for matching cyan pixels inside Region A
        cyan_match = np.where(
            (img_np[:, :, 0] == BUBBLE_COLOR[0]) & 
            (img_np[:, :, 1] == BUBBLE_COLOR[1]) & 
            (img_np[:, :, 2] == BUBBLE_COLOR[2])
        )
        
        if len(cyan_match[0]) > 0:
            print("2. Notice: Cyan bubbles detected! Pulling the hook.")
            pyautogui.click()
            bite_detected = True
            break
            
    if not bite_detected or not fishing:
        continue

    # --------------------------------------
    # STEPS 3 & 4: Reeling Initialization
    # --------------------------------------
    print("3. Action: Entering Reeling State.")
    scope_of_green = None
    start_reeling_time = time.time()
    last_click_time = 0
    fish_caught = False
    reeling_pause = False

    # --------------------------------------
    # STEP 4: Reeling Loop (Auto-Clicking & Color Evaluation)
    # --------------------------------------
    while fishing and not fish_caught:
        if keyboard.is_pressed('q'):
            toggle_fishing()
            break

        current_time = time.time()

        # Handle Reeling/Auto-clicking logic if not paused
        if not reeling_pause:
            if current_time - last_click_time >= CLICK_INTERVAL:
                pyautogui.click()
                last_click_time = current_time

        # Optimized UI snapshot for checking conditions
        ui_snapshot = ImageGrab.grab(bbox=UI_BBOX)

        # Helper function to get color mapping relative to UI local space
        def get_local_color(global_pt):
            return ui_snapshot.getpixel((global_pt[0] - UI_BBOX[0], global_pt[1] - UI_BBOX[1]))

        # Evaluate scope of green availability after 0.25 seconds
        if scope_of_green is None and (current_time - start_reeling_time >= TIMER_CONDITION):
            if get_local_color(GH_POINT) == GREY_COLOR:
                scope_of_green = True
                print("4. Status: Scope of green is available.")

        # Interrupt checks when scope of green is established
        if scope_of_green == True:
            
            # (i) Condition: Fish Caught Check (Change from Grey at GH_POINT)
            if get_local_color(GH_POINT) != GREY_COLOR:
                # --------------------------------------
                # STEP 5: Fish caught
                # --------------------------------------
                print("5. Status: Scope of green is not available. Fish caught!")
                scope_of_green = False
                fish_caught = True
                break

            # (ii) Condition: Red Zone Trigger (Pause Reeling)
            if not reeling_pause:
                red_triggered = False
                for pt in RED_ZONE:
                    if get_local_color(pt) == WHITE_COLOR:
                        red_triggered = True
                        break
                
                if red_triggered:
                    # --------------------------------------
                    # STEP 6: Reeling pause
                    # --------------------------------------
                    print("4. Interrupt: RED_ZONE turned white. Entering Reeling Pause.")
                    reeling_pause = True

        # Handle Pause evaluation
        if reeling_pause and fishing:
            green_triggered = False
            for pt in GREEN_ZONE:
                if get_local_color(pt) == WHITE_COLOR:
                    green_triggered = True
                    break
            
            if green_triggered:
                print("6. Status: GREEN_ZONE turned white. Resuming Reeling.")
                reeling_pause = False
                last_click_time = time.time() # Instantly triggers click on loop reset

    # --------------------------------------
    # STEP 7: Reset & Repeat
    # --------------------------------------
    if fish_caught:
        print("7. Action: Resetting checkpoints. Preparing next cast...\n")
        time.sleep(1.5)  # Pause to let catch UI clear out securely