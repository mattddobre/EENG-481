import random
import time
from enum import Enum
from gpiozero import DistanceSensor
from gpiozero.exc import DistanceSensorNoEcho
import robot_api as robot


# =========================
# Configuration
# =========================

OBSTACLE_DISTANCE_CM = 25
WALL_DISTANCE_CM = 20

STEP_TIME = 0.05
SENSOR_DELAY = 0.05

MIN_SPEED = 220
MAX_SPEED = 350

# Forward behavior (SHORTER)
MIN_FORWARD_TIME = 0.5
MAX_FORWARD_TIME = 1.5
FORWARD_CONTINUE_PROB = 0.05   # Much less straight chaining

# Turning behavior (LARGER + MORE FREQUENT)
MIN_TURN_ANGLE = 20
MAX_TURN_ANGLE = 90
TURN_MEAN = 45
TURN_STD_DEV = 25

# Avoidance
BACKUP_SPEED = 250
BACKUP_DURATION = 0.6

TURN_SPEED = 300
TURN_180_DURATION = 1.6


# =========================
# Sensors
# =========================

sensor_front = DistanceSensor(echo=24, trigger=23, max_distance=2)
sensor_left  = DistanceSensor(echo=22, trigger=27, max_distance=2)
sensor_right = DistanceSensor(echo=20, trigger=21, max_distance=2)
sensor_wl    = DistanceSensor(echo=19, trigger=26, max_distance=2)
sensor_wr    = DistanceSensor(echo=16, trigger=25, max_distance=2)


def read_sensor(sensor):
    try:
        return sensor.distance * 100
    except DistanceSensorNoEcho:
        return None


# =========================
# State Machine
# =========================

class State(Enum):
    WANDER_FORWARD = 1
    WANDER_TURN = 2
    AVOID_BACKUP = 3
    AVOID_TURN_180 = 4
    AVOID_WALL_TURN = 5


state = State.WANDER_FORWARD
state_timer = 0
target_duration = 0
wall_turn_direction = None


# =========================
# Motion Helpers
# =========================

def duration_for_angle(angle):
    return (angle / 180.0) * TURN_180_DURATION


def set_forward(speed):
    robot._apply_motor_values(speed, speed, speed, speed)


def set_pivot_left(speed):
    robot._apply_motor_values(-speed, -speed, speed, speed)


def set_pivot_right(speed):
    robot._apply_motor_values(speed, speed, -speed, -speed)


def biased_turn_angle():
    while True:
        angle = random.gauss(TURN_MEAN, TURN_STD_DEV)
        if MIN_TURN_ANGLE <= abs(angle) <= MAX_TURN_ANGLE:
            return abs(angle)


# =========================
# Detection
# =========================

def obstacle_detected():
    front = read_sensor(sensor_front)
    time.sleep(SENSOR_DELAY)

    left = read_sensor(sensor_left)
    time.sleep(SENSOR_DELAY)

    right = read_sensor(sensor_right)
    time.sleep(SENSOR_DELAY)

    for d in [front, left, right]:
        if d is not None and d < OBSTACLE_DISTANCE_CM:
            return True
    return False


def wall_detected():
    wl = read_sensor(sensor_wl)
    time.sleep(SENSOR_DELAY)

    wr = read_sensor(sensor_wr)
    time.sleep(SENSOR_DELAY)

    if wl is not None and wl < WALL_DISTANCE_CM:
        return "left"

    if wr is not None and wr < WALL_DISTANCE_CM:
        return "right"

    return None


# =========================
# Main Loop
# =========================

print("Starting autonomous robot (more turning)... CTRL+C to stop")

try:
    while True:

        # =========================
        # Interrupts
        # =========================

        if state in [State.WANDER_FORWARD, State.WANDER_TURN]:

            if obstacle_detected():
                robot.stop()
                state = State.AVOID_BACKUP
                state_timer = 0
                continue

            wall_side = wall_detected()
            if wall_side:
                robot.stop()
                wall_turn_direction = wall_side
                state = State.AVOID_WALL_TURN
                state_timer = 0
                continue


        # =========================
        # STATE LOGIC
        # =========================

        if state == State.WANDER_FORWARD:

            if state_timer == 0:
                speed = random.randint(MIN_SPEED, MAX_SPEED)
                target_duration = random.uniform(MIN_FORWARD_TIME, MAX_FORWARD_TIME)
                print("STATE: FORWARD")

            set_forward(speed)
            state_timer += STEP_TIME

            if state_timer >= target_duration:
                robot.stop()
                state_timer = 0

                if random.random() < FORWARD_CONTINUE_PROB:
                    state = State.WANDER_FORWARD
                else:
                    state = State.WANDER_TURN


        elif state == State.WANDER_TURN:

            if state_timer == 0:
                speed = random.randint(MIN_SPEED, MAX_SPEED)
                angle = biased_turn_angle()
                target_duration = duration_for_angle(angle)
                turn_direction = random.choice(["left", "right"])
                print(f"STATE: TURN {turn_direction.upper()} {angle:.1f}°")

            if turn_direction == "left":
                set_pivot_left(speed)
            else:
                set_pivot_right(speed)

            state_timer += STEP_TIME

            if state_timer >= target_duration:
                robot.stop()
                state = State.WANDER_FORWARD
                state_timer = 0


        elif state == State.AVOID_BACKUP:

            if state_timer == 0:
                print("STATE: BACKUP")

            robot._apply_motor_values(
                -BACKUP_SPEED,
                -BACKUP_SPEED,
                -BACKUP_SPEED,
                -BACKUP_SPEED
            )

            state_timer += STEP_TIME

            if state_timer >= BACKUP_DURATION:
                robot.stop()
                state = State.AVOID_TURN_180
                state_timer = 0


        elif state == State.AVOID_TURN_180:

            if state_timer == 0:
                print("STATE: TURN 180°")

            set_pivot_left(TURN_SPEED)

            state_timer += STEP_TIME

            if state_timer >= TURN_180_DURATION:
                robot.stop()
                state = State.WANDER_FORWARD
                state_timer = 0


        elif state == State.AVOID_WALL_TURN:

            if state_timer == 0:
                print(f"STATE: WALL AVOID from {wall_turn_direction.upper()}")
                target_duration = duration_for_angle(90)

            if wall_turn_direction == "left":
                set_pivot_right(TURN_SPEED)
            else:
                set_pivot_left(TURN_SPEED)

            state_timer += STEP_TIME

            if state_timer >= target_duration:
                robot.stop()
                state = State.WANDER_FORWARD
                state_timer = 0


        time.sleep(STEP_TIME)


except KeyboardInterrupt:
    print("\nStopping robot.")
    robot.stop()
