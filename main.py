import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils, drawing_styles
import numpy as np
import time

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")

options = vision.HandLandmarkerOptions(
    base_options = base_options,
    num_hands = 2,
    min_hand_detection_confidence = 0.5,
    min_tracking_confidence = 0.5,
    running_mode = vision.RunningMode.VIDEO
)

landmarker = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    timestamp_ms = time.monotonic_ns() // 1_000_000
    detection_results = landmarker.detect_for_video(mp_image, timestamp_ms)

    annotated_image = np.copy(frame)

    for hand_landmarks in detection_results.hand_landmarks:
        drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks,
            vision.HandLandmarksConnections.HAND_CONNECTIONS,
            drawing_styles.get_default_hand_landmarks_style(),
            drawing_styles.get_default_hand_connections_style()
        )

    cv2.imshow("webcam", cv2.flip(annotated_image, 1))


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
