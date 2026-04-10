  AeroMouse: A High Percision Gesture-Based HCI System.
Built with Python, OpenCV, and Mediapipe to bridge the gap between human motion and digital control.

******* DISCLAIMER & SAFETY GUIDELINES *******
AeroMouse uses real-time computer vision and heuristic logic. Because it relies on speed, lighting conditions, and camera frames, please beware of the following:
  Experimental AI: This is a prototype-system. Frame drops or background noise (reflections, multiple hands in the same frame, complex lighting,...) can occasionally cause
   unintened clicks or movements.
  Safety First: I highly recommend you to test this program in a "sandbox" environment first (like an empty notepad, or an empty browser) before using it for high-stakes tasks.

  If you are reviewing this for admissions or professional evaluation, please ensure you dont have sensitive, unsaved work in the background! Id truely hate for a left-click
  to accidentally close your browser and loose your progress!!! (⓿_⓿)

  Emergency Kill-Switch: Put your hand out of the frame, click on the program, while the webcam is showing, press "q" on your keyboard.
  Secondary Kill-Switch: When navigating with your hand, smashing the mouse into the top-left corner of your screen will interrupt the program.
  
*****************************************************

Functions:
  . Movement of the Mouse: For this function, i implemented an exponential power curve (Δx^1.35) to convert fast and slow hand movement into cursor velocity.
    This provides pixel-perfect percision for small movements, and high-velocity traversal for fast movements.
  . Left Click: The left click function works by pretending to pinch something using the index and thumb. The system tracks a "pre-click" phase, as the fingers become closer,
     and therefore dynamically lowers the sensitivity of the mouse, eventually dampened to 0 the moment a pinch is detected, eliminating "click-slip".
  . Scrolling: By holding your index and middle finger connected to one another, the software will allow you to scroll up/ down depending on what direction the fingers are pointing.
     This function required the integration of a distance-based toggle between Navigation Mode(moving), Click Mode, and Scroll Mode by analyzing the relationship between the middle and index finger.
  . Tab Switch: You are able to switch to your previous tab with moving your hand with all fingers open left/right fast. This function needed the usage of a python "deque" history
     of the previous 4 frames to perform real-time pattern matching for a swipe gesture (Alt+Tab), in order to distinguish between a swipe and random hand gestures.

Requirements:
    Python 3.x
    A Webcam.
Installation:
  1. Clone the repository within your terminal:
        git clone https://github.com/Madacool01/AeroMouse.git
  2. Within your terminal, navigate to the directory:
        cd "AeroMouse 04.10.2026"
  3. Create a virtual Environment:
        Windows:
        python -m venv venv
        .\venv\Scripts\activate

        Mac/Linux:
        python3 -m venv venv
        source venv/bin/activate

4. Install the required libaries:
    pip install -r requirements.txt
5. Ensure your webcam is connected and run the main script:
    python main.py.
6. HAVE FUN AND EXPERIMENT!!!!!!!


    
