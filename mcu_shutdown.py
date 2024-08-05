import subprocess
import time
import os
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

def get_gpio_state(pin):
    try:
        result = subprocess.run(['raspi-gpio', 'get', str(pin)], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            logging.debug(f"GPIO {pin} state: {output}")
            # Extract the level from the output
            if "level=1" in output:
                return 1
            else:
                return 0
        else:
            logging.error(f"Failed to get properties for GPIO {pin}: {result.stderr.strip()}")
            return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

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

    low_start_time = None

    while True:
        current_state_delay = get_gpio_state(GPIO_PIN_SHUTDOWN_DELAY)
        current_state_immediate = get_gpio_state(GPIO_PIN_SHUTDOWN_IMMEDIATE)

        if current_state_delay is None or current_state_immediate is None:
            logging.error("Failed to read GPIO state. Exiting.")
            break

        # Check for immediate shutdown (polarity changed: high = shutdown)
        if current_state_immediate == 1:
            logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_IMMEDIATE} is HIGH. Shutting down the host immediately...")
            # give time to moonrake to do it's stuff
            time.sleep(20)
            shutdown_host()
            return

        # Check for delayed shutdown
        if current_state_delay == 0:
            if low_start_time is None:
                low_start_time = time.time()
                logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_DELAY} went LOW. Starting timer.")
        else:
            if low_start_time is not None:
                low_start_time = None
                logging.debug(f"GPIO pin {GPIO_PIN_SHUTDOWN_DELAY} went HIGH. Resetting timer.")

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
