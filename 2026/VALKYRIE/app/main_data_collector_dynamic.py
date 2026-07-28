import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import csv
import os


#-----------CONFIGURATION------------
ACTIVE_EXERCISE = "Pushup"
side_facing_camera = "Right"

EXERCISE_FEATURES = {
    "Pushup": ["elbow_angle", "hip_angle", "body_tilt", "arm_raise_angle", "squat_vertical_angle", "triangle_area"],
    "Squat": ["elbow_angle", "hip_angle", "body_tilt", "arm_raise_angle", "squat_vertical_angle", "knee_angle"]
}

#------------INITIALIZATION------------


base_dir = os.path.dirname(os.path.abspath(__file__))
task_file_path = os.path.join(base_dir, "pose_landmarker_lite.task")
data_file_path = os.path.join(base_dir, "..", "data", f"{ACTIVE_EXERCISE.lower()}_data.csv")

header = ["class"]+EXERCISE_FEATURES[ACTIVE_EXERCISE]
if not os.path.exists(data_file_path):
    with open(data_file_path, mode="w", newline="") as f:
        csv.writer(f).writerow(header)


#----------FUNCTIONS-------------
def calculate_angle_old(a, b, c):
    v1 = np.arctan2(a[1] - b[1], a[0] - b[0])
    v2 = np.arctan2(c[1] - b[1], c[0] - b[0])

    radians = v1 - v2
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - 180

    return angle

def calculate_triangle_area(s, h, a):
    A = np.abs(s[0]*(h[1]-a[1]) + h[0]*(a[1]-s[1]) + a[0]*(s[1]-h[1]))
    A /= 2
    return A

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)


def vertical_horizontal_angle(x2, x1, y2, y1):
    radians = np.arctan2(y2-y1, x2-x1)

    angle = np.abs(radians* 180 / np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle

#-----------MEDIAPIPE SETUP------------

# Standard MediaPipe Pose skeleton connections
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), # Shoulders and arms
    (11, 23), (12, 24), (23, 24),                   # Torso
    (23, 25), (24, 26), (25, 27), (26, 28),         # Legs
    (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32) # Feet
]



latest_result = None

def set_results(results):
    global latest_result
    latest_result = results


base_options = python.BaseOptions(model_asset_path=task_file_path)
options =  vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=lambda result, output_image, timestamp_ms: set_results(result)
)

#----------VARIABLES-----------

excersise_counter = 0
excersise_stage = None

is_recording = False
current_excersise_record = None
file_handle = None

duration_limit = 15

#----------MAIN LOOP-------------
with vision.PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        key = cv2.waitKey(1)

        if key & 0xFF == ord("s"):
            time.sleep(5)
            is_recording = not is_recording
            if is_recording:
                start_time = time.perf_counter()
            current_excersise_record = f"Bad_{ACTIVE_EXERCISE}"
            if is_recording:
                file_handle = open(data_file_path, mode='a', newline="")
            elif not is_recording:
                if file_handle:
                    file_handle.close()
                    file_handle = None
        
        if key & 0xFF == ord("q"):
            break

        if is_recording:
            current_duration = time.perf_counter() - start_time

            if current_duration >= duration_limit:
                print("Time up!")
                break

        success, image = cap.read()
        if not success: break

        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp = int(time.time() * 1000)
        landmarker.detect_async(mp_image, timestamp)

        if latest_result and latest_result.pose_landmarks:
            h, w, _ = image.shape
            for landmarks in latest_result.pose_landmarks:


                if side_facing_camera == "Right":
                    shoulder = [landmarks[12].x, landmarks[12].y]
                    elbow = [landmarks[14].x, landmarks[14].y]
                    wrist = [landmarks[16].x, landmarks[16].y]
                    hip = [landmarks[24].x, landmarks[24].y]
                    knee = [landmarks[26].x, landmarks[26].y]
                    ankle = [landmarks[28].x, landmarks[28].y]

                elif side_facing_camera == "Left":
                    shoulder = [landmarks[11].x, landmarks[11].y]
                    elbow = [landmarks[13].x, landmarks[13].y]
                    wrist = [landmarks[15].x, landmarks[15].y]
                    hip = [landmarks[23].x, landmarks[23].y]
                    knee = [landmarks[25].x, landmarks[25].y]
                    ankle = [landmarks[27].x, landmarks[27].y]

                elbow_angle = calculate_angle(shoulder, elbow, wrist)
                hip_angle = calculate_angle(shoulder, hip, knee)
                knee_angle = calculate_angle(ankle, knee, hip)    
                body_tilt = np.arctan2(hip[1] - shoulder[1], hip[0] - shoulder[0])
                body_tilt = np.abs(body_tilt * 180.0 / np.pi)
                arm_raise_angle = calculate_angle(hip, shoulder, elbow)
                squat_vertical_angle = vertical_horizontal_angle(y2=shoulder[1], y1=hip[1], x2=shoulder[0], x1=hip[0])
                triangle_area = calculate_triangle_area(shoulder, hip, ankle)

                all_data = {
                    "elbow_angle":elbow_angle,
                    "hip_angle": hip_angle,
                    "body_tilt": body_tilt,
                    "arm_raise_angle": arm_raise_angle,
                    "squat_vertical_angle": squat_vertical_angle,
                    "knee_angle": knee_angle,
                    "triangle_area":triangle_area
                }


                required_features = EXERCISE_FEATURES[ACTIVE_EXERCISE]
                row = [all_data[key] for key in required_features]



                if is_recording and file_handle:
                    csv_writer = csv.writer(file_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow([current_excersise_record]+ row)
                    print(f"Successfully logged {current_excersise_record} rep!")
                    
                if is_recording:
                    cv2.putText(image, "RECORDING DATA...", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (87, 209, 0), 3)
                else:
                    cv2.putText(image, "READY TO RECORD...", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 119), 3)
              

                cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)

                cv2.rectangle(image, (0,90), (225, 166), (245,117,16), -1)

                cv2.putText(image, str(knee_angle),
                    (10, 150),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)


                cv2.putText(image, str(excersise_counter), 
                    (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)


                # ********************** DRAWING ************************
                # 1. Draw the connection lines
                for start_idx, end_idx in POSE_CONNECTIONS:
                    start = landmarks[start_idx]
                    end = landmarks[end_idx]
                    
                    # Convert normalized coordinates to pixel coordinates
                    pt1 = (int(start.x * w), int(start.y * h))
                    pt2 = (int(end.x * w), int(end.y * h))
                    
                    cv2.line(image, pt1, pt2, (0, 255, 0), 2)

                # 2. Draw the landmark dots
                for landmark in landmarks:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(image, (cx, cy), 3, (0, 0, 255), -1)

        cv2.imshow("AI Sport Ref", image)
if file_handle:
    file_handle.close()
    print("File saved safely.")


cap.release()
cv2.destroyAllWindows()