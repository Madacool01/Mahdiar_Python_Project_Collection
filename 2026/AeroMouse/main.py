import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import pyautogui as pag
from collections import deque


latest_result = None

def distance(x2, x1, y2, y1):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

def result_getback(result, output_image, timestamps_ms):
    global latest_result
    latest_result = result

base = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base,
    running_mode = vision.RunningMode.LIVE_STREAM,
    num_hands = 1,
    result_callback=result_getback,
)

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),    # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),    # Index
    (0, 9), (9, 10), (10, 11), (11, 12), # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky
]

detector = vision.HandLandmarker.create_from_options(options)

# save_frames_x = []
# save_frames_y = []

counter = 0

size = pag.size()

pag.moveTo(x=size[0]/2, y=size[1]/2)

is_clicking = False

x_history = deque(maxlen=4)

webcam = cv2.VideoCapture(0)
while webcam.isOpened():
    if cv2.waitKey(5) & 0xFF == ord("q"):
        break



    success, image = webcam.read()
    if not success: break

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    current_timestamp = int(time.time() * 1000)

    detector.detect_async(mp_image, current_timestamp)


    if latest_result and latest_result.hand_landmarks:
        for hand_landmarks in latest_result.hand_landmarks:
            index_finger_tip = hand_landmarks[8]
            thumb_finger_tip = hand_landmarks[4]
            middle_finger_tip = hand_landmarks[12]
            wrist = hand_landmarks[0]
            middle_knuckle = hand_landmarks[9]

            x_pixel_thumb = (1-thumb_finger_tip.x)
            y_pixel_thumb = thumb_finger_tip.y
            z_pixel_thumb = thumb_finger_tip.z

            x_pixel_middle = (1-middle_finger_tip.x)
            y_pixel_middle = middle_finger_tip.y

            x_pixel_index = (1-index_finger_tip.x)
            y_pixel_index = index_finger_tip.y
            z_pixel_index = index_finger_tip.z

            x_pixel_knuckle = (1-middle_knuckle.x)
            y_pixel_knuckle = middle_knuckle.y

            x_pixel_wrist = (1-wrist.x)
            y_pixel_wrist = wrist.y

            x_history.append(x_pixel_index)

            dist_wrist_knuckle = distance(x_pixel_wrist, x_pixel_knuckle, y_pixel_wrist, y_pixel_knuckle)
            dist_wrist_middle = distance(x_pixel_wrist, x_pixel_middle, y_pixel_wrist, y_pixel_middle)

            if dist_wrist_knuckle < dist_wrist_middle:
                if len(x_history) > 3:
                    swipe_distance = x_pixel_index-x_history[0]
                    x_history.clear()
                    if swipe_distance > 0.5:
                        pag.hotkey("alt", "tab")
                        time.sleep(0.5)
                    elif swipe_distance < -0.5:
                        pag.hotkey("alt", "tab")
                        time.sleep(0.5)

            # If the swipe_distance is greater than a range, or less than a range, it means we have swiped to the left/right.

            

            if counter == 0:
                current_x = x_pixel_index
                prev_x = x_pixel_index
                current_y = y_pixel_index
                prev_y = y_pixel_index
            else:
                current_x = x_pixel_index
                current_y = y_pixel_index

            dx = current_x-prev_x
            dy = current_y-prev_y

            distance_index_middle = ((x_pixel_index-x_pixel_middle)**2 + (y_pixel_index-y_pixel_middle)**2)**0.5
            distance_index_thumb = ((x_pixel_index-x_pixel_thumb)**2 + (y_pixel_index-y_pixel_thumb)**2 + (z_pixel_index-z_pixel_thumb)**2)**0.5

            sensitivity = 8000
            scroll_sensitivity = 700

            if 0.02 < distance_index_middle < 0.07: # Scroll Mode
                scroll_speed = int(dy * scroll_sensitivity)*-1
                pag.scroll(scroll_speed)

            else:
                # **************** DONT TOUCH!!!! ****************
                if 0.02 < distance_index_thumb < 0.06 and is_clicking is False: # Click Mode
                    current_sen = 0  # Full Freeze of the mouse
                    pag.leftClick()
                    time.sleep(0.3)
                    dx = 0
                    dy = 0
                    is_clicking = True

                elif distance_index_thumb < 0.035:
                    current_sen = sensitivity * 0.1 # Becoming slower and precise ready for pinch
                    is_clicking = True
                else: # Move mode
                    current_sen = sensitivity
                    # pag.mouseUp() # This mouseDown/Up concept doesnt work as well?!
                    is_clicking = False

                    #******************* DONT TOUCH! ***************************

                    sign_dx = 1 if dx > 0 else -1
                    sign_dy = 1 if dy > 0 else -1

                    abs_dx = abs(dx)
                    abs_dy = abs(dy)


                    exponent = 1.35
                    scale_x = (abs_dx**exponent) * current_sen
                    scale_y = (abs_dy**exponent) * current_sen

                    mouse_move_x = scale_x*sign_dx
                    mouse_move_y = scale_y * sign_dy

                    pag.moveRel(xOffset=mouse_move_x, yOffset=mouse_move_y)
                    prev_x = current_x
                    prev_y = current_y
                # **************** DO NOT TOUCH! *******************
                    
            



            for start_idx, end_idx in CONNECTIONS:
                start = hand_landmarks[start_idx]
                end = hand_landmarks[end_idx]
                pt1 = (int(start.x * image.shape[1]), int(start.y * image.shape[0]))
                pt2 = (int(end.x * image.shape[1]), int(end.y * image.shape[0]))
                cv2.line(image, pt1, pt2, (0, 255, 0), 2)
            
            # Draw nodes (joints)
            for landmark in hand_landmarks:
                cx, cy = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
                cv2.circle(image, (cx, cy), 5, (255, 0, 0), -1)
            counter+=1


    cv2.imshow("Hand Tracker", image)


webcam.release()
cv2.destroyAllWindows()