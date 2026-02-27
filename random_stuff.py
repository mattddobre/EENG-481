import time
from IIC2 import (
    MOTOR_TYPE,
    set_motor_parameter,
    control_speed,
    control_pwm
)

# =========================
# Configuration
# =========================

DEFAULT_SPEED = 300      # Adjust based on your robot
TURN_SPEED = 300         # Speed used for turning
MOVE_DURATION = 1.0      # Move for 1 second
TURN_DURATION = 0.6      # Adjust until robot turns ~90 degrees

_initialized = False


# =========================
# Internal Helpers
# =========================

def _initialize():
    global _initialized
    if not _initialized:
        set_motor_parameter()
        _initialized = True


def _apply_motor_values(m1, m2, m3, m4):
    if MOTOR_TYPE == 4:
        control_pwm(m1, m2, m3, m4)
    else:
        control_speed(m1, m2, m3, m4)


def _stop():
    _apply_motor_values(0, 0, 0, 0)


# =========================
# Public API Functions
# =========================

def move_forward(speed=DEFAULT_SPEED):
    """
    Move forward for 1 second.
    """
    _initialize()
    _apply_motor_values(speed, speed, speed, speed)
    time.sleep(MOVE_DURATION)
    _stop()


def move_backward(speed=DEFAULT_SPEED):
    """
    Move backward for 1 second.
    """
    _initialize()
    _apply_motor_values(-speed, -speed, -speed, -speed)
    time.sleep(MOVE_DURATION)
    _stop()


def turn_left(speed=TURN_SPEED):
    """
    Turn left 90 degrees, then move forward for 1 second.
    """
    _initialize()

    # Rotate left in place
    _apply_motor_values(-speed, -speed, speed, speed)
    time.sleep(TURN_DURATION)
    _stop()
    time.sleep(0.2)

    # Move forward after turning
    move_forward(speed)


def turn_right(speed=TURN_SPEED):
    """
    Turn right 90 degrees, then move forward for 1 second.
    """
    _initialize()

    # Rotate right in place
    _apply_motor_values(speed, speed, -speed, -speed)
    time.sleep(TURN_DURATION)
    _stop()
    time.sleep(0.2)

    # Move forward after turning
    move_forward(speed)
    
    


import cv2
import numpy as np
from libcamera import Transform
from picamera2 import Picamera2

# Initialize camera
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Background subtractor for motion detection
backsub = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25)

# Threshold: how big a moving object must be to be considered "too close"
CLOSE_AREA_THRESHOLD = 50000   # adjust based on your camera and distance

print("Running... press Ctrl+C to stop")

while True:
    frame = picam2.capture_array()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect motion
    fgmask = backsub.apply(gray)

    # Clean noise
    kernel = np.ones((5, 5), np.uint8)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area > CLOSE_AREA_THRESHOLD:
            print("⚠️ WARNING: Object extremely close to camera!")
            cv2.putText(frame, "WARNING: TOO CLOSE!", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Draw contour for visualization
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Show preview
    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
