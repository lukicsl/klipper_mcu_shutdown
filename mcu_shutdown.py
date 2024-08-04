import RPi.GPIO as GPIO
import time
import os
import subprocess

# Define GPIO pins
GPIO_PIN_SHUTDOWN_DELAY = 26
GPIO_PIN_SHUTDOWN_IMMEDIATE = 13

# Duration in seconds for which the GPIO must remain low to trigger shutdown
LOW_DURATION_THRESHOLD = int(os.getenv('LOW_DURATION_THRESHOLD', 10))

# Setup GPIO
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_SHUTDOWN_DELAY, GPIO.IN)  # No pull-up or pull-down
GPIO.setup(GPIO_PIN_SHUTDOWN_IMMEDIATE, GPIO.IN)  # No pull-up or pull-down

def shutdown_host():
    try:
        # Execute systemctl command to shut down the host
        subprocess.run(['systemctl', 'poweroff'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to shut down the host: {e}")

def check_gpio():
    last_state_delay = GPIO.input(GPIO_PIN_SHUTDOWN_DELAY)
    low_start_time = None

    while True:
        current_state_delay = GPIO.input(GPIO_PIN_SHUTDOWN_DELAY)
        current_state_immediate = GPIO.input(GPIO_PIN_SHUTDOWN_IMMEDIATE)

        # Check for immediate shutdown
        if current_state_immediate == GPIO.LOW:
            print(f"GPIO pin {GPIO_PIN_SHUTDOWN_IMMEDIATE} is LOW. Shutting down the host immediately...")
            shutdown_host()
            return

        # Check for delayed shutdown
        if current_state_delay != last_state_delay:
            if current_state_delay == GPIO.LOW:
                low_start_time = time.time()
            else:
                low_start_time = None

            last_state_delay = current_state_delay
        
        if low_start_time and (time.time() - low_start_time >= LOW_DURATION_THRESHOLD):
            print(f"GPIO pin {GPIO_PIN_SHUTDOWN_DELAY} is LOW for {LOW_DURATION_THRESHOLD} seconds. Shutting down the host...")
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
    finally:
        GPIO.cleanup()  # Clean up GPIO settings
