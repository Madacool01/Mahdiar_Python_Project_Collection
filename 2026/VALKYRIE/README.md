# VALKYRIE

A real-time posture analysis and workout tracking app. It monitors your exercise form through a webcam, counts reps, gives live corrections, and manages sets and rest timers.

---

## Features

- **Live pose tracking** — tracks key body landmarks (elbows, hips, knees, shoulders) in real time using MediaPipe pose estimation
- **Form detection** — a trained Random Forest model tells good form from bad form
- **Live coaching cues** — gets specific feedback like *"Lower your chest closer to the floor"* or *"Lower your hips"* when bad technique is caught
- **Automatic rep and set counting** — counts reps based on joint angle changes and tracks sets as you go
- **Workout timers** — set up sets, reps, and rest time, with popups and a confetti animation when you finish
- **Built-in exercise guides** — form tips and injury warnings baked into the app
- **Desktop GUI** — built with `customtkinter`, with light, dark, and system appearance modes

---

## Installation

### Prerequisites

- Python 3.9–3.11
- A webcam

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-fitness-coach.git
cd ai-fitness-coach
```

Or download the repo as a ZIP, extract it, and open a terminal inside the folder.

### 2. Create a virtual environment

**Windows**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install customtkinter opencv-python mediapipe numpy pandas scikit-learn Pillow
```

### 4. Check model files are in place

| File | Location |
|---|---|
| `pose_landmarker_full.task` | `app/` |
| `pushup_model.pkl` | `models/` |
| `squat_model.pkl` | `models/` |

### 5. Run it

```bash
cd app
python fitness_dashboard.py
```

---

## How to Use

1. Position your webcam so your full body is visible from the side (left or right facing)
2. Pick an exercise from the dropdown (Pushups, Squats)
3. Check the **Exercise Guide** button for form tips and injury warnings
4. Set your sets, reps per set, and rest time
5. Click **Commence** and start your reps — the app counts valid reps, flags bad form live, and starts a rest countdown automatically between sets
