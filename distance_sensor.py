from gpiozero import DistanceSensor
from time import sleep

# echo pin first, trigger pin second
sensor = DistanceSensor(echo=24, trigger=23)

while True:
    distance_cm = sensor.distance * 100  # convert from meters to cm
    print(f"Distance: {distance_cm:.2f} cm")
    sleep(1)