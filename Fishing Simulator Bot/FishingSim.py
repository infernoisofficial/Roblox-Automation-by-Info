import pyautogui
import keyboard
import time
from PIL import ImageGrab

# --- CONFIGURATION & PATHS ---
MARKER_IMAGE_PATH = r"D:\Games\Roblox-Automation-by-Info\Fishing Simulator Bot\Marker.png"

# --- COORDINATES & REGIONS ---
# Region A format for pyautogui: (left, top, width, height)
# (150, 150) to (1710, 893) -> width = 1710-150 = 1560, height = 893-150 = 743
REGION_A = (150, 150, 1560, 743)

# Specific coordinate points
POINT_XY = (1031, 820)
POINT_UV = (941, 819)
POINT_EF = (729, 756)

# --- COLORS (RGB) ---
CYAN_COLOR = (68, 252, 234)
WHITE_COLOR = (255, 255, 255)
GREEN_COLOR = (83, 255, 83)  # Fixed typo 259 to 255 (max RGB value)
RED_COLOR = (251, 98, 76)

# --- CONFIDENCE & SETTINGS ---
COLOR_TOLERANCE = 15  # Variable for color confidence allowance
IMAGE_CONFIDENCE = 0.8
CLICK_INTERVAL = 0.01  # 10 milliseconds delay

# --- STATE MANAGEMENT ---
fishing_active = False
is_hook_thrown = False
green_appeared = False

def color_matches(c1, c2, tolerance=COLOR_TOLERANCE):
    """Checks if two colors match within a specific tolerance/confidence range."""
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def toggle_fishing():
    global fishing_active
    fishing_active = not fishing_active
    print(f"\n[TOGGLE] Fishing State changed! Active = {fishing_active}")
    if not fishing_active:
        print("[INFO] Bot paused. Press 'Q' to resume.")

# Register 'Q' as the toggle key
keyboard.add_hotkey('q', toggle_fishing)

print("=== Fishing Bot Initialized ===")
print("Press 'Q' to Start/Pause the bot.")

# --- MAIN LOOP ---
while True:
    # Small sleep to prevent high CPU utilization
    time.sleep(0.05)

    if not fishing_active:
        continue

    # STEP 1: Throw Hook
    if not is_hook_thrown:
        print("[STEP 1] Throwing Hook...")
        # Clicking inside Region A to throw the hook
        pyautogui.click(x=960, y=540) 
        is_hook_thrown = True
        green_appeared = False
        time.sleep(2) # Wait for hook animation to settle
        print("[STEP 2] Waiting for Cyan bubbles in Region A...")

    # STEP 2: Wait for Cyan bubbles to pull
    else:
        # Locate the capsule-shaped marker to ensure UI is ready
        marker_pos = pyautogui.locateOnScreen(MARKER_IMAGE_PATH, confidence=IMAGE_CONFIDENCE)
        
        # Take a quick screenshot of Region A to search for cyan pixels
        screen_a = ImageGrab.grab(bbox=(REGION_A[0], REGION_A[1], REGION_A[0] + REGION_A[2], REGION_A[1] + REGION_A[3]))
        pixels = screen_a.getdata()
        
        cyan_detected = False
        for px in pixels:
            if color_matches(px, CYAN_COLOR):
                cyan_detected = True
                break
        
        if cyan_detected:
            print("[BITE!] Cyan detected! Pulling hook...")
            pyautogui.click() # Initial pull click
            time.sleep(0.5)   # Wait for reeling UI to appear
            
            print("[STEP 3/4] Reeling Phase Started...")
            # Reeling Loop
            while fishing_active:
                # Track if green color has appeared at (e,f) to initiate step 5 check
                ef_pixel = pyautogui.pixel(POINT_EF[0], POINT_EF[1])
                if color_matches(ef_pixel, GREEN_COLOR):
                    green_appeared = True

                # STEP 5: Fish Caught Check (Green disappeared at e,f after appearing)
                if green_appeared and not color_matches(ef_pixel, GREEN_COLOR):
                    print("[SUCCESS] Green disappeared at (e,f). Fish Caught!")
                    is_hook_thrown = False # Resets to step 1/repeat step 2
                    time.sleep(1)
                    break

                # STEP 3 & 4: Reeling and Pause Mechanics
                # Locate marker to check dynamically on the x-axis
                current_marker = pyautogui.locateOnScreen(MARKER_IMAGE_PATH, confidence=IMAGE_CONFIDENCE)
                if current_marker:
                    # 'Right side means x axis + 1' -> Looking at the pixel just right of the marker bounding box
                    right_side_x = current_marker.left + current_marker.width + 1
                    right_side_y = current_marker.top + (current_marker.height // 2)
                    
                    try:
                        right_pixel = pyautogui.pixel(right_side_x, right_side_y)
                        
                        # Step 4: Reeling Pause if Right Side is Red
                        if color_matches(right_pixel, RED_COLOR):
                            # Do nothing, pause reeling
                            time.sleep(0.05)
                            continue
                        
                        # Step 3: Reel if Right Side is Green
                        elif color_matches(right_pixel, GREEN_COLOR):
                            pyautogui.click()
                            time.sleep(CLICK_INTERVAL) # 10ms load delay
                    except Exception:
                        # Fail-safe if coordinates jump out of bounds temporarily
                        pass