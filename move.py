from smbus2 import SMBus
import time

I2C_ADDR = 0x26
RUN_REG = 0x06

def set_motor(bus, motor_id, speed, direction=0, param=10):
    data = [motor_id, speed, direction, param]
    bus.write_i2c_block_data(I2C_ADDR, RUN_REG, data)

def stop_motor(bus, motor_id):
    # Correct STOP/BRAKE command for Yahboom motor driver
    data = [motor_id, 0, 2, 0]
    bus.write_i2c_block_data(I2C_ADDR, RUN_REG, data)

with SMBus(1) as bus:
    print("Starting motor slowly...")

    # Slow speed (try 40–70 for gentle rotation)
    set_motor(bus, motor_id=1, speed=0, direction=0)

    input("Motor is spinning. Press ENTER to stop...\n")

    print("Stopping motor...")
    stop_motor(bus, 1)
    time.sleep(0.2)

print("Done.")

