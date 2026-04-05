AI Posture App:

This is an App that I made for it to track my posture, spinal health, and digital eye strain during long coding sessions (e.g Projects, Competitive Programming,...)
This app utilizes Mediapipe's BlazeFace model for lightweight, real-time tracking. This project implements a Z-axis Proxy by calculating the Euclidean distance between the corners of the users eye at users default sitting position.
This is done through the press of a Global Hotkey (Ctrl+Alt+s), and this allows the user to personalize their default distance.
Lastly, the Program actively calculates the current distance between the users eyes, and whenever the distance exceeds *1.8 the default threshhold, the user is met with a red warning window that tells the user to sit back to their default posture, and it later then removed when the distance is within the range of our threshold.
The Temporary red Window is created using a Transparent GUI overlay using Tkinter. The window uses Z-Order Managment (Always on top) to ensure visibilty across all apps.

**** Optimizations: ******
The input resolution has been reduced to 320 x 240 pixels. This decreased the computational complexity of the Program by up to 90%, significantly lowering CPU and Memory usage.
Furthermore, the program utilizes a 0.5s polling interval (a sleep logic). This allows the program to capture a frame to compute every 2 seconds, instead of the default 30 FPS, which is sufficient for human movement while perserving battery life.

*** How to use: ******
1. Run the script: Ensure Cv2, Mediapipe and pynput are installed! The webcam stays hidden for privacy and performance.
2. Calibrate: Sit with perfect posture and press "Ctrl+Alt+s".
3. Work: If you lean too close, the screen will trigger a red warning screen until you move back.



***** Lessons Learned, Struggles *****
1. Optimizing the program was firstly a challenge for me. The need to keep the camera hidden for performance and privacy made me unable to use cv2.waitKey() for taking in input, forcing me into learning how to use the GlobalHotkey command from Pynput.
2. Finding a safe zone vs. a "bad posture zone" required tons of test cases to find the perfect threshold for any user (I forced my parents into trying it our as well to take various eye distances into mind).
