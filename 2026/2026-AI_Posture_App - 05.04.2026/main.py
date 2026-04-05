import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tkinter as tk
from time import sleep, time
import pynput

base = python.BaseOptions(model_asset_path="blaze_face_short_range.tflite")
options = vision.FaceDetectorOptions(base_options=base)
detector = vision.FaceDetector.create_from_options(options)

webcam = cv2.VideoCapture(0)

should_calibrate = False

overlay = tk.Tk()
overlay.attributes("-fullscreen", True)
overlay.attributes("-topmost", True)
overlay.attributes("-alpha", True)
overlay.config(bg="#6F6F6F")
overlay.wm_attributes("-transparentcolor", "#6F6F6F")

time_leaned_in = 0

def on_activate():
    global should_calibrate
    should_calibrate = True

listener = pynput.keyboard.GlobalHotKeys({
    "<ctrl>+<alt>+s": on_activate
})
listener.start()

while webcam.isOpened():
    

    if cv2.waitKey(5) & 0xFF == ord("q"):
        break


    success, image = webcam.read()
    cv2.resize(image, dsize=(320, 240))


    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

    results = detector.detect(mp_image)

    ih, iw, _ = image.shape

    base_distance_list = 0


    if results.detections:
        for detection in results.detections:

            right_eye = detection.keypoints[0]
            left_eye = detection.keypoints[1]

            right_x, right_y = int(right_eye.x * iw), int(right_eye.y * ih)
            left_x, left_y = int(left_eye.x * iw), int(right_eye.y * ih)

            current_distance = ((right_x-left_x)**2+(left_y-right_y)**2)**0.5



            if should_calibrate:

                
                is_blured = False
                should_calibrate = False

                base_line_distance = ((right_x-left_x)**2+(left_y-right_y)**2)**0.5
                base_distance_list = base_line_distance

                # flash_end_time = time()+2

                # if time() < flash_end_time:
                overlay.lift()
                overlay.config(bg="#00FF80")
                success_label = tk.Label(overlay, text="Base Distance Calibrated Successfully!", bg="#00FF80")
                success_label.place(relx=0.5, rely=0.5, anchor="center")
                overlay.attributes("-alpha", 1.0)
                overlay.update()
                sleep(2)
                overlay.attributes("-alpha", 0.0)

            try:
                if base_line_distance is not None:     
                    if current_distance > base_line_distance*1.8 and is_blured is False:
                        time_leaned_in += 3
                        if time_leaned_in > 3:
                            time_leaned_in = 0
                            overlay.lift()
                            overlay.config(bg="red")
                            is_blured = True
                            #Blur
                            overlay.attributes("-alpha", 0.6)
                            too_close = tk.Label(overlay, text="You are too close to the screen!", font=("Times New Roman", 60, "bold"), bg="red")
                            too_close.place(relx=0.5, rely=0.5, anchor="center", height=100, width=12000)
                            overlay.update()

                                
                    elif current_distance < base_line_distance*1.5:
                        is_blured = False
                        #Remove Blur
                        overlay.attributes("-alpha", 0.0)
                        ...
        
            except NameError:
                pass
            box = detection.bounding_box
            cv2.rectangle(image, (box.origin_x, box.origin_y), 
                (box.origin_x + box.width, box.origin_y + box.height), 
                (0, 255, 0), 2)
            sleep(0.5)
            
    #Debug the fact that the program doesnt save when the webcam isnt showing.
    #Make a shortcut (Ctrl+Alt+S) for saving so you dont accidentally trigger a save by just pressing s.
    # cv2.imshow("Mahdiar",image)



