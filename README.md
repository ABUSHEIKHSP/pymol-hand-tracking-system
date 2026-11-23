# PyMOL Hand Tracking System

Control molecular structures in [PyMOL](https://pymol.org/) using hand gestures captured through a webcam. The project uses MediaPipe Gesture Recognizer to track hand landmarks and recognize a closed-fist gesture, while OpenCV captures and displays the camera feed.

## Features

- **Single-hand rotation:** Move your index fingertip horizontally or vertically to rotate the structure around PyMOL's Y or X axis.
- **Two-hand zoom:** Move your hands apart or closer together to zoom in or out.
- **Fist gesture lock:** Make a closed fist with either detected hand to pause all PyMOL movement commands.
- **Hand landmark visualization:** View detected hand landmarks and connections in the webcam window.
- **Local processing:** Webcam frames and gesture recognition are processed locally using OpenCV and MediaPipe.

## How It Works

The application processes webcam frames in a continuous loop:

1. OpenCV reads a frame from the selected webcam.
2. The frame is converted from BGR to RGB and wrapped as a MediaPipe image.
3. MediaPipe Gesture Recognizer detects up to two hands, estimates their landmarks, and classifies gestures.
4. The application checks whether any detected hand is classified as `Closed_Fist`.
5. If a fist is detected, movement commands are skipped and the previous tracking positions are reset.
6. Otherwise, hand landmarks are used to determine whether to rotate or zoom the PyMOL structure.
7. PyMOL receives commands through its XML-RPC interface.

## Gesture Controls

| Hand gesture / movement | PyMOL action |
| --- | --- |
| One hand: move index fingertip left or right | Rotate around the Y axis |
| One hand: move index fingertip up or down | Rotate around the X axis |
| Two hands: move hands apart | Zoom in |
| Two hands: move hands closer together | Zoom out |
| Either hand: make a closed fist | Pause all movement |

### Landmark Usage

MediaPipe returns 21 landmarks for each detected hand. The current implementation uses:

| Landmark index | Landmark | Purpose |
| ---: | --- | --- |
| `1` | Thumb CMC | Used as the two-hand zoom reference point |
| `8` | Index fingertip | Used for single-hand rotation |

The two-hand zoom distance is calculated from the normalized `x` and `y` coordinates of landmark `1` from each hand.

### Motion Thresholds

The current thresholds and command steps are configured near the top of `main.py`:

| Parameter | Current value | Purpose |
| --- | ---: | --- |
| `ROTATION_THRESHOLD` | `0.02` | Minimum normalized fingertip movement required to trigger rotation |
| `ZOOM_THRESHOLD` | `0.017` | Minimum change in normalized distance between the two hand reference points required to trigger zoom |
| `ROTATION_ANGLE` | `20` | Rotation step in degrees for each triggered command |
| `ZOOM_STEP` | `17` | Zoom movement step sent to PyMOL |

These values can be adjusted in `main.py` to change control sensitivity.

## Requirements

- Python
- A webcam
- [PyMOL](https://pymol.org/) with its XML-RPC server enabled
- OpenCV
- MediaPipe

Python dependencies are listed in `requirements.txt`: `opencv-python` and `mediapipe`.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ABUSHEIKHSP/pymol-hand-tracking-system.git
cd pymol-hand-tracking-system
```

### 2. Create and activate a virtual environment

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the MediaPipe Gesture Recognizer model

The application expects the Gesture Recognizer model bundle at `gesture_recognizer.task` in the project root.

Download it with:

```bash
curl -L "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task" -o gesture_recognizer.task
```

The model file is excluded from version control by `.gitignore` (`*.task`), so it must be downloaded locally before running the application.

## Running the Application

### 1. Start PyMOL with XML-RPC enabled

Start PyMOL with its remote-control server enabled:

```bash
pymol -R
```

The application connects to the XML-RPC server at `http://localhost:9123`. Keep PyMOL running while using the hand-tracking application.

### 2. Start the hand-tracking application

In a separate terminal, from the project directory with the virtual environment activated:

```bash
python main.py
```

The webcam window displays the camera feed with detected hand landmarks. Use the gestures in the control table to interact with the structure in PyMOL.

Press **q** while the webcam window is focused to exit the application.

## Project Structure

```text
pymol-hand-tracking-system/
├── main.py                 # Webcam capture, hand tracking, gesture recognition, and PyMOL controls
├── requirements.txt        # Python dependencies
├── gesture_recognizer.task # MediaPipe Gesture Recognizer model (download separately)
├── .gitignore              # Excludes virtual environment, model bundles, and test files
└── README.md
```

## Troubleshooting

### PyMOL connection refused

- Make sure PyMOL is running with XML-RPC enabled using `pymol -R`.
- Confirm the server is available at `http://localhost:9123`.
- Start PyMOL before launching `main.py`.

### Gesture Recognizer model not found

- Confirm that `gesture_recognizer.task` exists in the project root.
- Check that the filename matches the `model_asset_path` configured in `main.py`.

### Webcam does not open

- Check that the webcam is connected and available to the operating system.
- The current implementation opens camera index `0` using `cv2.VideoCapture(0)`. Change the index if your webcam uses a different device index.
- Ensure that no other application is exclusively using the webcam.

### Hand gestures are not detected reliably

- Use sufficient, even lighting.
- Keep the hand visible within the camera frame.
- Avoid covering the fingers and palm.
- Adjust `min_hand_detection_confidence` and `min_tracking_confidence` in `main.py` if necessary.

### Controls feel too sensitive or not sensitive enough

Adjust `ROTATION_THRESHOLD`, `ZOOM_THRESHOLD`, `ROTATION_ANGLE`, and `ZOOM_STEP` in `main.py`. Smaller thresholds cause more frequent movement commands; larger thresholds require more hand movement.

## Notes

- The current application supports one-hand rotation and two-hand zoom.
- Gesture recognition and hand landmark tracking are performed by MediaPipe.
- PyMOL commands are sent over the local XML-RPC connection.
- The application currently uses camera index `0` and assumes the PyMOL XML-RPC server is available at `localhost:9123`.

## License

No license file is currently included in this repository. Unless a license is added, the repository's contents are not explicitly licensed for reuse or redistribution.