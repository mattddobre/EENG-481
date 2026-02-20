from gpiozero import Button
import subprocess
import signal
import time

button = Button(17, pull_up=True)

process = None
running = False

def toggle():
    global process, running

    if not running:
        print("Starting robot script...")
        process = subprocess.Popen(["python3", "test_api.py"])
        running = True
    else:
        print("Stopping robot script...")
        process.send_signal(signal.SIGINT)
        process.wait()
        running = False

button.when_pressed = toggle

print("Waiting for button press...")
while True:
    time.sleep(1)
