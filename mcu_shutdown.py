# import RPi.GPIO as GPIO
import time
import os
import signal
import sys

while True
    time.sleep(1)

# Configuration
GPIO_PIN = 26
LOW_DURATION_THRESHOLD = int(os.getenv('LOW_DURATION_THRESHOLD', 10))  # Default to 10 seconds if not set

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Global variable to control the running state
running = True

def handle_signal(signal_number, frame):
    global running
    print(f"Received signal {signal_number}. Exiting gracefully...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_signal)  # Handle SIGTERM

def check_gpio():
    low_start_time = None
    while running:
        input_state = GPIO.input(GPIO_PIN)
        if input_state == GPIO.LOW:
            if low_start_time is None:
                low_start_time = time.time()
            elif (time.time() - low_start_time) >= LOW_DURATION_THRESHOLD:
                print("GPIO26 has been low for too long. Shutting down...")
                os.system("sudo shutdown -h now")
        else:
            low_start_time = None

        time.sleep(1)

try:
    check_gpio()
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    print("Cleaning up GPIO settings...")
    GPIO.cleanup()
    print("Exiting program.")
