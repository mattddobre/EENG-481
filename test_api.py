import time
from robot_api import move_forward, turn_left

def move_square_ccw():
    """
    Move the robot in a counterclockwise square.
    Each side is 1 forward movement (1 second).
    """

    print("Starting counterclockwise square test...")

    # Optional: move forward once before starting turns
    move_forward()

    # Complete 4 left turns (each includes forward motion)
    for i in range(1):
        time.sleep(0.5)
        turn_left()

    print("Square complete.")


if __name__ == "__main__":
    try:
        move_square_ccw()
    except KeyboardInterrupt:
        print("Test interrupted.")
