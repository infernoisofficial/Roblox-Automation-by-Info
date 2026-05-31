import time
import keyboard
import numpy as np
import pyautogui

# --- Configuration & Constants ---
pyautogui.PAUSE = 0  # Removes default pyautogui delay for fast clicking
pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort script

# Colors (R, G, B)
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
GREY_COLOR = (188, 188, 188)
GREEN_COLOR = (83, 250, 83)
RED_COLOR = (251, 98, 76)

# Script State
fishing = False


def toggle_fishing():
    global fishing
    fishing = not fishing
    print(f"\n--- Fishing State Changed: {'ENABLED' if fishing else 'DISABLED'} ---")
    if fishing:
        print("Starting fishing cycle...")
    time.sleep(0.3)  # Debounce delay


# Register the toggle key 'Q'
keyboard.add_hotkey("q", toggle_fishing)

print("=== Fishing Bot Initialized ===")
print("Press 'Q' to Toggle Fishing ON/OFF")
print("Move mouse to the top-left corner of the screen to Emergency Stop")

# --- Main Program Loop ---
while True:
    if not fishing:
        time.sleep(0.1)
        continue

    # Step 1: Throw hook
    print("Action: Throwing Hook...")
    pyautogui.click()
    time.sleep(1.0)  # Wait for hook animation to settle before scanning

    # Step 2: Wait for Bite (Look for Cyan pixels in Region A)
    print("Status: Waiting for bite (Scanning Region A)...")
    bite_detected = False

    while fishing and not bite_detected:
        # Region A: (100, 100) to (1750, 950) -> width=1650, height=850
        screenshot_a = pyautogui.screenshot(region=(100, 100, 1650, 850))
        img_a = np.array(screenshot_a)

        # Vectorized check for CYAN color matches
        cyan_mask = (
            (img_a[:, :, 0] == CYAN_COLOR[0])
            & (img_a[:, :, 1] == CYAN_COLOR[1])
            & (img_a[:, :, 2] == CYAN_COLOR[2])
        )

        if np.any(cyan_mask):
            print("Status: Bite Detected! Hooking...")
            pyautogui.click()  # Click to lock the bite
            bite_detected = True
            time.sleep(0.2)  # Short delay to transition into reeling phase

    # Step 4, 5, 6: Reeling and Reeling Pause System
    if fishing and bite_detected:
        print("Status: Entering Reeling Phase...")

        # Setup localized bounding box containing Region B, (g,h), and (e,f)
        # Min X = 1080, Max X = 1208 -> Capture width 140 (up to 1220)
        # Min Y = 757, Max Y = 892  -> Capture height 150 (from 750 to 900)
        box_x, box_y, box_w, box_h = 1080, 750, 140, 150

        # Function to capture the unified bounding box and return pixel information
        def get_game_data():
            img = np.array(pyautogui.screenshot(region=(box_x, box_y, box_w, box_h)))

            # 1. Extract specific point values using relative offsets
            # (g,h) = (1193, 766) -> Relative: x=113, y=16
            color_gh = tuple(img[16, 113])

            # (e,f) = (1208, 757) -> Relative: x=128, y=7
            color_ef = tuple(img[7, 128])

            # 2. Extract Region B patch -> (1080,798) to (1171,892)
            # Relative: Y from (798-750)=48 to (892-750)=142 | X from (1080-1080)=0 to (1171-1080)=91
            b_patch = img[48:142, 0:91]
            red_mask = (
                (b_patch[:, :, 0] == RED_COLOR[0])
                & (b_patch[:, :, 1] == RED_COLOR[1])
                & (b_patch[:, :, 2] == RED_COLOR[2])
            )
            white_mask = (
                (b_patch[:, :, 0] == WHITE_COLOR[0])
                & (b_patch[:, :, 1] == WHITE_COLOR[1])
                & (b_patch[:, :, 2] == WHITE_COLOR[2])
            )

            return color_gh, color_ef, np.sum(red_mask), np.sum(white_mask)

        # Initialize base state
        reeling_state = "reeling"
        _, _, base_red, base_white = get_game_data()

        last_click_time = time.time()
        last_check_time = time.time()

        # Inner loop tracking the reel progression
        while fishing:
            current_time = time.time()

            # 50 millisecond Autoclicker execution
            if reeling_state == "reeling" and (current_time - last_click_time) >= 0.1:
                pyautogui.click()
                last_click_time = current_time

            # 0.25 second Condition Check Execution (Timer Condition)
            if (current_time - last_check_time) >= 0.25:
                last_check_time = current_time

                # Fetch pixel states inside the targeted boundary box
                color_gh, color_ef, red_count, white_count = get_game_data()

                # Condition (i): Fish Caught Tracking
                if color_gh == GREY_COLOR:
                    print("scope of green is available")
                    if color_ef == GREEN_COLOR:
                        print("Fish caught!")
                        break  # Breaks out of reeling state machine to reset to step 1

                # Condition (ii): State transitions based on Region B shifts
                if reeling_state == "reeling":
                    # Look for decrease in red AND increase in white by 100 pixels
                    if (base_red - red_count >= 100) and (
                        white_count - base_white >= 100
                    ):
                        print("Reeling pause")
                        reeling_state = "pause"
                        base_red, base_white = red_count, white_count

                elif reeling_state == "pause":
                    # Look for increase in red AND decrease in white by 100 pixels
                    if (red_count - base_red >= 100) and (
                        base_white - white_count >= 100
                    ):
                        print("Reeling")
                        reeling_state = "reeling"
                        base_red, base_white = red_count, white_count

            # Tiny sleep to avoid CPU pinning without harming click intervals
            time.sleep(0.001)

    print("Cycle complete. Restarting in 2 seconds...")
    time.sleep(2.0)