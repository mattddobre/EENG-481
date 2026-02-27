import random
import time
from enum import Enum
from gpiozero import DistanceSensor
import robot_api as robot


# =========================
# Configuration
# =========================

OBSTACLE_DISTANCE_CM = 15
STEP_TIME = 0.05

MIN_SPEED = 220
MAX_SPEED = 350

MAX_TURN_ANGLE = 90
MIN_TURN_ANGLE = 15

BACKUP_SPEED = 250
BACKUP_DURATION = 0.6

TURN_AROUND_SPEED = 300
TURN_180_DURATION = 1.6  # Calibrate if needed
FORWARD_CONTINUE_PROB = 0.20   # 60% chance to keep going straight

sensor = DistanceSensor(echo=24, trigger=23)


# =========================
# State Machine
# =========================

class State(Enum):
    WANDER_FORWARD = 1
    WANDER_TURN = 2
    AVOID_BACKUP = 3
    AVOID_TURN = 4


state = State.WANDER_FORWARD
state_timer = 0
target_duration = 0


# =========================
# Helpers
# =========================

def obstacle_detected():
    return sensor.distance * 100 < OBSTACLE_DISTANCE_CM


def duration_for_angle(angle):
    return (angle / 180.0) * TURN_180_DURATION


def set_forward(speed):
    robot._apply_motor_values(speed, speed, speed, speed)


def set_pivot_left(speed):
    left, right = robot._compute_turn_speeds(speed, 0)
    robot._apply_motor_values(left, left, right, right)


def set_pivot_right(speed):
    left, right = robot._compute_turn_speeds(speed, 0)
    robot._apply_motor_values(right, right, left, left)
    
def biased_turn_angle():
    mean = 25            # center bias toward small turns
    std_dev = 20         # spread

    while True:
        angle = random.gauss(mean, std_dev)

        if MIN_TURN_ANGLE <= abs(angle) <= MAX_TURN_ANGLE:
            return angle


# =========================
# Main Controller Loop
# =========================

print("Starting FSM autonomous wandering... (CTRL+C to stop)")

try:

    while True:

        # Global obstacle interrupt (except during avoidance)
        if state in [State.WANDER_FORWARD, State.WANDER_TURN]:
            if obstacle_detected():
                robot.stop()
                state = State.AVOID_BACKUP
                state_timer = 0
                continue

        # =========================
        # STATE LOGIC
        # =========================

        if state == State.WANDER_FORWARD:

            if state_timer == 0:
                speed = random.randint(MIN_SPEED, MAX_SPEED)
                target_duration = random.uniform(1,3)
                print("STATE: FORWARD")
            
            set_forward(speed)

            state_timer += STEP_TIME

        if state_timer >= target_duration:
            robot.stop()
            state_timer = 0

            if random.random() < FORWARD_CONTINUE_PROB:
                # Stay in forward state
                state = State.WANDER_FORWARD
            else:
                # Switch to turning
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
                print("STATE: AVOID_BACKUP")

            robot._apply_motor_values(-BACKUP_SPEED,
                                      -BACKUP_SPEED,
                                      -BACKUP_SPEED,
                                      -BACKUP_SPEED)

            state_timer += STEP_TIME

            if state_timer >= BACKUP_DURATION:
                robot.stop()
                state = State.AVOID_TURN
                state_timer = 0

        elif state == State.AVOID_TURN:

            if state_timer == 0:
                print("STATE: AVOID_TURN 180°")

            set_pivot_left(TURN_AROUND_SPEED)

            state_timer += STEP_TIME

            if state_timer >= TURN_180_DURATION:
                robot.stop()
                state = State.WANDER_FORWARD
                state_timer = 0

        time.sleep(STEP_TIME)

except KeyboardInterrupt:
    print("\nStopping robot.")
    robot.stop()
