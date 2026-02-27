import cv2
import numpy as np
from picamera2 import Picamera2
import time

# ==========================
# CAMERA SETUP
# ==========================
picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (1280, 720)}   # Larger frame (less zoomed look)
)

picam2.configure(config)
picam2.start()

# ==========================
# DISTANCE CALIBRATION
# ==========================
KNOWN_WIDTH = 15.0      # cm (real object width)
FOCAL_LENGTH = 700.0    # <-- Recalibrate after changing resolution!

def estimate_distance(pixel_width):
    if pixel_width == 0:
        return 999
    return (KNOWN_WIDTH * FOCAL_LENGTH) / pixel_width

# ==========================
# PARAMETERS
# ==========================
MIN_AREA = 800            # Lowered so bottle isn't ignored
CLOSE_DISTANCE = 40       # cm threshold
CENTER_TOLERANCE = 100    # Wider center zone (since frame is bigger)

distance_buffer = []

print("Improved Vision System Running...")

try:
    while True:
        frame = picam2.capture_array()

        # FIX COLOR INVERSION (Picamera gives RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        frame_height, frame_width = frame.shape[:2]
        frame_center = frame_width // 2

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Improve contrast (helps clear bottles)
        gray = cv2.equalizeHist(gray)

        # Blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # More sensitive edge detection
        edges = cv2.Canny(blurred, 30, 100)

        # Connect broken edges
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        largest_object = None
        largest_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < MIN_AREA:
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            aspect_ratio = w / float(h)
            if aspect_ratio < 0.2 or aspect_ratio > 4:
                continue

            if area > largest_area:
                largest_area = area
                largest_object = (x, y, w, h)

        if largest_object is not None:
            x, y, w, h = largest_object
            object_center = x + w // 2

            distance = estimate_distance(w)

            # Smooth distance over last 5 frames
            distance_buffer.append(distance)
            if len(distance_buffer) > 5:
                distance_buffer.pop(0)

            smooth_distance = sum(distance_buffer) / len(distance_buffer)

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.putText(frame,
                        f"{int(smooth_distance)} cm",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)

            # Draw center tolerance lines
            cv2.line(frame,
                     (frame_center - CENTER_TOLERANCE, 0),
                     (frame_center - CENTER_TOLERANCE, frame_height),
                     (255, 0, 0), 2)

            cv2.line(frame,
                     (frame_center + CENTER_TOLERANCE, 0),
                     (frame_center + CENTER_TOLERANCE, frame_height),
                     (255, 0, 0), 2)

            # Collision decision
            if smooth_distance < CLOSE_DISTANCE:
                if object_center < frame_center - CENTER_TOLERANCE:
                    print("Obstacle LEFT - Should turn RIGHT")
                elif object_center > frame_center + CENTER_TOLERANCE:
                    print("Obstacle RIGHT - Should turn LEFT")
                else:
                    print("Obstacle CENTER - STOP")
            else:
                print("Path Clear")

        cv2.imshow("Improved Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cv2.destroyAllWindows()
    picam2.stop()
