import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import os
import pickle
import pandas as pd
from collections import Counter


#**********CONFIGURATION***********
ACTIVE_EXERCISE = "Squat"
side_facing_camera = "Right"

EXERCISE_MODEL_CONFIG = {
    "Squat" : "squat_model.pkl",
    "Pushup" : "pushup_model.pkl"
}

EXERCISE_RULES = {
    "Pushup" : {"down_angle": 85, "up_angle": 165, "check_parameter":"elbow_angle"},
    "Squat" : {"down_angle": 90, "up_angle": 160, "check_parameter":"knee_angle"}
}

EXERCISE_FEATURES = {
    "Squat": ["elbow_angle", "hip_angle", "body_tilt", "arm_raise_angle", "squat_vertical_angle", "knee_angle"],
    "Pushup": ["elbow_angle", "hip_angle", "body_tilt", "arm_raise_angle", "squat_vertical_angle", "triangle_area"]
}

FEEDBACK_CONFIG = {
    "Pushup": [  #If "parameter" "less" than "angle_limit": print("msg")
        {"parameter":"elbow_angle", "angle_limit": 100, "comparison":"greater", "msg": "Lower you chest closer to the floor"},
        {"parameter":"triangle_area", "angle_limit": 0.03, "comparison":"greater", "msg":"Lower your hips"} 
    ]
}



#-------INITIALIZATION--------

base_dir = os.path.dirname(os.path.abspath(__file__))
task_file_path = os.path.join(base_dir, "pose_landmarker_full.task")
model_filename = EXERCISE_MODEL_CONFIG[ACTIVE_EXERCISE]
model_path = os.path.join(base_dir, "..", "models", model_filename)

with open(model_path, "rb") as f:
    model = pickle.load(f)

excersise_counter = 0
excersise_stage = None
feedback = None


#--------FUNCTIONS----------

def increment_counter(excersise_name, current_angle, counter):
    global excersise_stage
    rules = EXERCISE_RULES[excersise_name]
    down_angle = rules["down_angle"]
    up_angle = rules["up_angle"]
    if current_angle < down_angle:
        excersise_stage = "down"
    if current_angle > up_angle and excersise_stage == "down":
        excersise_stage="up"
        counter+=1

    return counter

def calculate_triangle_area(s, h, a):
    A = np.abs(s[0]*(h[1]-a[1]) + h[0]*(a[1]-s[1]) + a[0]*(s[1]-h[1]))
    A /= 2
    return A

def calculate_angle_old(a, b, c):
    v1 = np.arctan2(a[1] - b[1], a[0] - b[0])
    v2 = np.arctan2(c[1] - b[1], c[0] - b[0])

    radians = v1 - v2
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

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

    
#--------MEDIAPIPE SETUP--------

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

prediction_history = []


#----------MAIN LOOP----------
with vision.PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success: break

        if cv2.waitKey(5) & 0xFF == ord("q"):break


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

                #------DYNAMIC MAPPING------.
                all_data = {
                    "elbow_angle":elbow_angle,
                    "hip_angle": hip_angle,
                    "body_tilt": body_tilt,
                    "arm_raise_angle": arm_raise_angle,
                    "squat_vertical_angle": squat_vertical_angle,
                    "knee_angle": knee_angle,
                    "triangle_area":triangle_area
                }

                current_active_angle = all_data[EXERCISE_RULES[ACTIVE_EXERCISE]["check_parameter"]] #Specific Angle for excersise.


                required_features = EXERCISE_FEATURES[ACTIVE_EXERCISE]
                filtered_data = {key: all_data[key] for key in required_features}

                features = pd.DataFrame([filtered_data])
                #-----PREDICTION------
                prediction = model.predict(features)[0]
                prediction_history.append(prediction)
                if len(prediction_history) > 20: prediction_history.pop(0)
                
                display_prediction = Counter(prediction_history).most_common(1)[0][0]

                if display_prediction == f"Bad_{current_active_angle}":
                    rules = FEEDBACK_CONFIG.get(ACTIVE_EXERCISE, [])

                    feedback = "Watch your form"

                    for rule in rules:
                        check_parameter = all_data[rule["parameter"]]
                        limit = rule["limit"]

                        violated = False
                        if rule["comparison"] == "less" and check_parameter < limit:
                            violated = True
                        elif rule["comparison"] == "greater" and check_parameter > limit:
                            violated = True

                        if violated:
                            feedback = rule["msg"]
                            break
                else:
                    feedback = "Good form"

                print(feedback)

                if display_prediction == f"Good_{ACTIVE_EXERCISE}":
                    excersise_counter = increment_counter(ACTIVE_EXERCISE, current_active_angle, excersise_counter)


                cv2.putText(image, f"Form: {display_prediction}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(image, f"REPS: {excersise_counter}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
                # cv2.putText(image, f"{EXERCISE_RULES[ACTIVE_EXERCISE]["check_parameter"]}: {current_active_angle}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                cv2.putText(image, f"HIP_ANGLE: {hip_angle}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)


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

cap.release()
cv2.destroyAllWindows()