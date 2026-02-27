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

DEFAULT_SPEED = 300
MOVE_DURATION = 1.0

TRACK_WIDTH = 0.16   # Distance between left & right wheels (meters)
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
    # Convert to integers BEFORE sending to driver
    m1 = int(round(m1))
    m2 = int(round(m2))
    m3 = int(round(m3))
    m4 = int(round(m4))

    if MOTOR_TYPE == 4:
        control_pwm(m1, m2, m3, m4)
    else:
        control_speed(m1, m2, m3, m4)


def _stop():
    _apply_motor_values(0, 0, 0, 0)

def stop():
    """
    Immediately stop all motors.
    """
    _initialize()
    _stop()

# =========================
# Core Motion Math
# =========================

def _compute_turn_speeds(speed, radius):
    """
    Returns left_speed, right_speed
    radius > 0  → turning left
    radius < 0  → turning right
    radius = 0  → in-place pivot
    """

    if radius == 0:
        # In-place rotation
        return -speed, speed

    R = abs(radius)
    W = TRACK_WIDTH

    left = speed * (R - W/2) / R
    right = speed * (R + W/2) / R

    if radius > 0:
        # turning left
        return left, right
    else:
        # turning right
        return right, left


# =========================
# Public API
# =========================

def move_forward(speed=DEFAULT_SPEED, duration=MOVE_DURATION):
    _initialize()
    _apply_motor_values(speed, speed, speed, speed)
    time.sleep(duration)
    _stop()


def move_backward(speed=DEFAULT_SPEED, duration=MOVE_DURATION):
    _initialize()
    _apply_motor_values(-speed, -speed, -speed, -speed)
    time.sleep(duration)
    _stop()


def turn_left(radius, speed=DEFAULT_SPEED, duration=MOVE_DURATION):
    """
    Continuous left turn with specified radius (meters).
    radius = 0 → pivot turn
    """
    _initialize()

    left_speed, right_speed = _compute_turn_speeds(speed, abs(radius))

    _apply_motor_values(left_speed, left_speed,
                        right_speed, right_speed)

    time.sleep(duration)
    _stop()


def turn_right(radius, speed=DEFAULT_SPEED, duration=MOVE_DURATION):
    """
    Continuous right turn with specified radius (meters).
    radius = 0 → pivot turn
    """
    _initialize()

    left_speed, right_speed = _compute_turn_speeds(speed, -abs(radius))

    _apply_motor_values(left_speed, left_speed,
                        right_speed, right_speed)

    time.sleep(duration)
    _stop()



