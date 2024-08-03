import RPi.GPIO as GPIO
import time
import os
import subprocess

# Define GPIO pin
GPIO_PIN = 26

# Duration in seconds for which the GPIO must remain low to trigger shutdown
LOW_DURATION_THRESHOLD = int(os.getenv('LOW_DURATION_THRESHOLD', 10))

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shutdown_host():
    try:
        # Execute systemctl command to shut down the host
        subprocess.run(['systemctl', 'poweroff'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to shut down the host: {e}")

def check_gpio():
    last_state = GPIO.input(GPIO_PIN)
    low_start_time = None

    while True:
        current_state = GPIO.input(GPIO_PIN)
        if current_state != last_state:
            if current_state == GPIO.LOW:
                low_start_time = time.time()
            else:
                low_start_time = None

            last_state = current_state
        
        if low_start_time and (time.time() - low_start_time >= LOW_DURATION_THRESHOLD):
            print("GPIO pin {} is LOW for {} seconds. Shutting down the host...".format(GPIO_PIN, LOW_DURATION_THRESHOLD))
            shutdown_host()
            return

        time.sleep(1)

if __name__ == "__main__":
    try:
        check_gpio()
    except KeyboardInterrupt:
        print("Program interrupted.")
    except Exception as e:
        print(f"An error occurred: {e}")
