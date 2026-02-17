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
