from gpiozero import Button
import subprocess
import signal
import time
import threading
import sys

# =========================
# Configuration
# =========================

BUTTON_PIN = 17
ROBOT_SCRIPT = "test_api.py"
SOUND_SCRIPT = "sound.py"

BOUNCE_TIME = 0.3
MIN_PRESS_INTERVAL = 1.0
LONG_PRESS_TIME = 3.0
ENABLE_DOUBLE_PRESS_RESTART = True

# =========================
# Hardware Setup
# =========================

button = Button(BUTTON_PIN, pull_up=True, bounce_time=BOUNCE_TIME)

robot_process = None
sound_process = None
running = False
last_press_time = 0
last_short_press_time = 0
exit_requested = False

# =========================
# Process Management
# =========================

def start_robot():
    global robot_process, sound_process, running
    if running:
        return
    print("Starting robot script...")
    robot_process = subprocess.Popen(["python3", ROBOT_SCRIPT])
    print("Starting sound script...")
    sound_process = subprocess.Popen(["python3", SOUND_SCRIPT])
    running = True

def stop_robot():
    global robot_process, sound_process, running
    if robot_process and running:
        print("Stopping robot script...")
        robot_process.send_signal(signal.SIGINT)
        robot_process.wait()
        robot_process = None
    if sound_process:
        print("Stopping sound script...")
        sound_process.send_signal(signal.SIGINT)
        sound_process.wait()
        sound_process = None
    running = False

def restart_robot():
    print("Restarting robot and sound scripts...")
    stop_robot()
    time.sleep(0.5)
    start_robot()

# =========================
# Watchdog Thread
# =========================

def watchdog():
    global running, robot_process, sound_process
    while True:
        if running:
            if robot_process and robot_process.poll() is not None:
                print("Robot process exited unexpectedly!")
                stop_robot()
        time.sleep(1)

threading.Thread(target=watchdog, daemon=True).start()

# =========================
# Button Handlers
# =========================

def handle_short_press():
    global last_press_time, last_short_press_time
    now = time.time()

    if now - last_press_time < MIN_PRESS_INTERVAL:
        return
    last_press_time = now

    # Double press detection
    if ENABLE_DOUBLE_PRESS_RESTART:
        if now - last_short_press_time < 0.6:
            restart_robot()
            last_short_press_time = 0
            return
    last_short_press_time = now

    # Toggle start/stop
    if not running:
        start_robot()
    else:
        stop_robot()

def handle_long_press():
    global exit_requested
    print("Long press detected — exiting controller")
    stop_robot()
    exit_requested = True

button.when_pressed = handle_short_press
button.when_held = handle_long_press
button.hold_time = LONG_PRESS_TIME

# =========================
# Main Loop
# =========================

print("Robot controller ready.")
print("Short press: Start/Stop")
print("Double press: Restart (if enabled)")
print("Long press (3s): Exit controller")

try:
    while not exit_requested:
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nCtrl+C detected.")

finally:
    print("Exiting controller.")
    stop_robot()
    sys.exit(0)
