import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils, drawing_styles
import numpy as np
import time
from xmlrpc import client
import math

# Connect to pymol via remote procedure call server
pymol = client.ServerProxy("http://localhost:9123")

ROTATION_THRESHOLD = 0.02
ZOOM_THRESHOLD = 0.017
ROTATION_ANGLE = 20
ZOOM_STEP = 17
previous_index_x = None
previous_index_y = None
previous_distance = None

# Mediaipipe
base_options = python.BaseOptions(model_asset_path="gesture_recognizer.task")

options = vision.GestureRecognizerOptions(
    base_options = base_options,
    num_hands = 2,
    min_hand_detection_confidence = 0.1,
    min_tracking_confidence = 0.1,
    running_mode = vision.RunningMode.VIDEO
)

recognizer = vision.GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    timestamp_ms = time.monotonic_ns() // 1_000_000
    detection_results = recognizer.recognize_for_video(mp_image, timestamp_ms)
    print(detection_results.gestures)
    fist_detected = any(
        gestures and gestures[0].category_name == "Closed_Fist"
        for gestures in detection_results.gestures
    )

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

    if fist_detected:
        print("fist detected")
        previous_index_x = None
        previous_index_y = None
        previous_distance = None
    else:
        # Pymol rotation implementation
        hands = detection_results.hand_landmarks 

        # [0] -> right hand, [6] -> index finger coordinates, .x -> from x, y, z, get x
        if len(hands) == 1:
            index_x = hands[0][8].x
            index_y = hands[0][8].y

            if previous_index_x is None:
                previous_index_x = index_x

            if previous_index_y is None:
                previous_index_y = index_y        

            if abs(index_x - previous_index_x) >= ROTATION_THRESHOLD:
                pymol.do(f"turn y, -{ROTATION_ANGLE}" if index_x > previous_index_x else f"turn y, {ROTATION_ANGLE}")

            if abs(index_y - previous_index_y) >= ROTATION_THRESHOLD:
                pymol.do(f"turn x, {ROTATION_ANGLE}" if index_y > previous_index_y else f"turn x, -{ROTATION_ANGLE}")

            previous_index_x = index_x
            previous_index_y = index_y

        elif len(hands) == 2:
            first_index = hands[0][1]
            second_index = hands[1][1]

            current_distance = math.dist(
                (first_index.x, first_index.y),
                (second_index.x, second_index.y)
            )

            if previous_distance is None:
                previous_distance = current_distance   

            if abs(current_distance - previous_distance) >= ZOOM_THRESHOLD:
                pymol.do(f"move z, {ZOOM_STEP}" if current_distance > previous_distance else f"move z, -{ZOOM_STEP}")

            previous_distance = current_distance

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
