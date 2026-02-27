import random
import time
from gpiozero import DistanceSensor
import robot_api as robot


# =========================
# Configuration
# =========================

# Motion settings
MIN_RADIUS = 0.0
MAX_RADIUS = 1.0
MIN_DURATION = 0.5
MAX_DURATION = 2.0

MIN_SPEED = 200
MAX_SPEED = 400

STEP_TIME = 0.05   # sensor check interval (50ms)

# Obstacle detection
OBSTACLE_DISTANCE_CM = 20

# Backup behavior
BACKUP_SPEED = 250
BACKUP_DURATION = 0.6

# 180° turn calibration (tune if needed)
TURN_AROUND_SPEED = 300
TURN_180_DURATION = 1.8

# Distance sensor
sensor = DistanceSensor(echo=24, trigger=23)


# =========================
# Safe Motion Function
# =========================

def safe_motion(action, speed, duration, radius=None):
    """
    Executes motion in small time slices while continuously
    checking for obstacles.
    Returns False if obstacle detected.
    """

    elapsed = 0

    while elapsed < duration:

        distance_cm = sensor.distance * 100

        if distance_cm < OBSTACLE_DISTANCE_CM:
            robot.stop()
            return False

        if action == "forward":
            robot._apply_motor_values(speed, speed, speed, speed)

        elif action == "left":
            left_speed, right_speed = robot._compute_turn_speeds(speed, abs(radius))
            robot._apply_motor_values(left_speed, left_speed,
                                      right_speed, right_speed)

        elif action == "right":
            left_speed, right_speed = robot._compute_turn_speeds(speed, -abs(radius))
            robot._apply_motor_values(left_speed, left_speed,
                                      right_speed, right_speed)

        time.sleep(STEP_TIME)
        elapsed += STEP_TIME

    robot.stop()
    return True


# =========================
# Obstacle Avoidance
# =========================

def avoid_obstacle():

    print("Obstacle detected! Executing avoidance maneuver.")

    # 1️⃣ Stop immediately
    robot.stop()
    time.sleep(0.2)

    # 2️⃣ Back up (NO obstacle checking here)
    print("Backing up...")
    robot._apply_motor_values(-BACKUP_SPEED,
                              -BACKUP_SPEED,
                              -BACKUP_SPEED,
                              -BACKUP_SPEED)
    time.sleep(BACKUP_DURATION)
    robot.stop()
    time.sleep(0.3)

    # 3️⃣ Turn 180° (pivot, no checking)
    print("Turning 180°...")
    left_speed, right_speed = robot._compute_turn_speeds(
        TURN_AROUND_SPEED,
        0   # pivot
    )

    robot._apply_motor_values(left_speed, left_speed,
                              right_speed, right_speed)

    time.sleep(TURN_180_DURATION)
    robot.stop()

    time.sleep(0.5)


# =========================
# Random Motion Loop
# =========================

def random_motion_loop():

    print("Starting SAFE obstacle-aware wandering... (CTRL+C to stop)")

    try:
        while True:

            action = random.choice(["forward", "left", "right"])
            speed = random.randint(MIN_SPEED, MAX_SPEED)
            duration = random.uniform(MIN_DURATION, MAX_DURATION)

            if action == "forward":
                print(f"FORWARD | speed={speed} duration={duration:.2f}")
                success = safe_motion("forward", speed, duration)

            elif action == "left":
                radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
                print(f"LEFT | radius={radius:.2f}")
                success = safe_motion("left", speed, duration, radius)

            elif action == "right":
                radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
                print(f"RIGHT | radius={radius:.2f}")
                success = safe_motion("right", speed, duration, radius)

            if not success:
                avoid_obstacle()

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nStopping robot.")
        robot.stop()


if __name__ == "__main__":
    random_motion_loop()
