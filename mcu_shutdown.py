import RPi.GPIO as GPIO
import time
import os
import subprocess
import logging

# Define GPIO pins
GPIO_PIN_SHUTDOWN_DELAY = 26
GPIO_PIN_SHUTDOWN_IMMEDIATE = 13

# Duration in seconds for which the GPIO must remain low to trigger shutdown
LOW_DURATION_THRESHOLD = int(os.getenv('LOW_DURATION_THRESHOLD', 10))

# Initial delay in seconds to disable shutdown logic
INITIAL_DELAY = 60

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup GPIO
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_SHUTDOWN_DELAY, GPIO.IN)  # No pull-up or pull-down
GPIO.setup(GPIO_PIN_SHUTDOWN_IMMEDIATE, GPIO.IN)  # No pull-up or pull-down

def shutdown_host():
    try:
        # Execute systemctl command to shut down the host
        logging.debug("Executing shutdown command.")
        subprocess.run(['systemctl', 'poweroff'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to shut down the host: {e}")

def check_gpio():
    # Initial delay to disable shutdown logic
    logging.debug(f"Initial delay of {INITIAL_DELAY} seconds. Shutdown logic will be disabled during this period.")
    time.sleep(INITIAL_DELAY)
    logging.debug("Initial delay period is over. Shutdown logic is now enabled.")

    last_state_delay = GPIO.input(GPIO_PIN_SHUTDOWN_DELAY)
    low_start_time = None

    while True:
        current_state_delay = GPIO.input(GPIO_PIN_SHUTDOWN_DELAY)
        current_state_immediate = GPIO.input(GPIO_PIN_SHUTDOWN_IMMEDIATE)

        logging.debug(f"GPIO_PIN_SHUTDOWN_DELAY state: {current_state_delay}")
        logging.debug(f"GPIO_PIN_SHUTDOWN_IMMEDIATE state: {current_state_immediate}")

        # Check for immediate shutdown (polarity changed: high = shutdown)
        if current_state_immediate == GPIO.HIGH:
            logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_IMMEDIATE} is HIGH. Shutting down the host immediately...")
            shutdown_host()
            return

        # Check for delayed shutdown
        if current_state_delay != last_state_delay:
            if current_state_delay == GPIO.LOW:
                low_start_time = time.time()
                logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_DELAY} went LOW. Starting timer.")
            else:
                low_start_time = None
                logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_DELAY} went HIGH. Resetting timer.")

            last_state_delay = current_state_delay
        
        if low_start_time and (time.time() - low_start_time >= LOW_DURATION_THRESHOLD):
            logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_DELAY} is LOW for {LOW_DURATION_THRESHOLD} seconds. Shutting down the host...")
            shutdown_host()
            return

        time.sleep(1)

if __name__ == "__main__":
    try:
        check_gpio()
    except KeyboardInterrupt:
        logging.info("Program interrupted.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings
        logging.debug("GPIO cleanup done.")
