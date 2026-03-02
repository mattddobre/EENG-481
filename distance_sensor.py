import time
from gpiozero import DistanceSensor
from gpiozero.exc import DistanceSensorNoEcho

# =========================
# Sensor Setup
# =========================

sensor_front = DistanceSensor(echo=24, trigger=23, max_distance=2)
sensor_left  = DistanceSensor(echo=22, trigger=27, max_distance=2)
sensor_right = DistanceSensor(echo=20, trigger=21, max_distance=2)
sensor_wl = DistanceSensor(echo=19, trigger=26, max_distance=2)
sensor_wr= DistanceSensor(echo=16, trigger=25, max_distance=2)
print("Sequential 3-Sensor Test (CTRL+C to stop)")
print("-" * 50)

def read_sensor(sensor):
    try:
        return sensor.distance * 100
    except DistanceSensorNoEcho:
        return None

try:
    while True:

        # Read one at a time
        front_cm = read_sensor(sensor_front)
        time.sleep(0.05)

        left_cm = read_sensor(sensor_left)
        time.sleep(0.05)

        right_cm = read_sensor(sensor_right)
        time.sleep(0.05)
        
        wr_cm= read_sensor(sensor_wr)
        time.sleep(0.05)
        
        wl_cm= read_sensor(sensor_wl)
        time.sleep(0.05)


        # Safe printing
        def fmt(value):
            return f"{value:6.1f} cm" if value is not None else "  ---  "

        print(
            f"Front: {fmt(front_cm)} | "
            f"Left: {fmt(left_cm)} | "
            f"Right: {fmt(right_cm)}"
            f"WR: {fmt(wr_cm)} | "
            f"WL: {fmt(wl_cm)} | "
        )

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopping sensor test.")
