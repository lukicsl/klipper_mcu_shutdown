import subprocess
import time
import os
import logging

# Define GPIO pins
GPIO_PIN_AUTO_SHUTDOWN = 26
GPIO_PIN_MANUAL_SHUTDOWN = 13

# Duration in seconds for which the GPIO must remain low to trigger shutdown
AUTO_OFF_DELAY = int(os.getenv('AUTO_OFF_DELAY', 10))
MANUAL_OFF_DELAY = int(os.getenv('MANUAL_OFF_DELAY', 10))

# Initial delay in seconds to disable shutdown logic
INITIAL_DELAY = 60

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_gpio_state(pin):
    try:
        result = subprocess.run(['raspi-gpio', 'get', str(pin)], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
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
        subprocess.run(['systemctl', 'poweroff'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to shut down the host: {e}")

def check_gpio():
    # Initial delay to disable shutdown logic
    logging.debug(f"Initial delay of {INITIAL_DELAY} seconds. Shutdown logic will be disabled during this period.")
    time.sleep(INITIAL_DELAY)
    logging.debug("Initial delay period is over. Shutdown logic is now enabled.")

    low_start_time_auto = None
    high_start_time_manual = None

    while True:
        current_state_auto = get_gpio_state(GPIO_PIN_AUTO_SHUTDOWN)
        current_state_manual = get_gpio_state(GPIO_PIN_MANUAL_SHUTDOWN)

        if current_state_auto is None or current_state_manual is None:
            logging.error("Failed to read GPIO state. Exiting.")
            break

        # Check for delayed shutdown for GPIO_PIN_AUTO_SHUTDOWN (when pin goes low)
        if current_state_auto == 0:
            if low_start_time_auto is None:
                low_start_time_auto = time.time()
        else:
            low_start_time_auto = None

        if low_start_time_auto and (time.time() - low_start_time_auto >= AUTO_OFF_DELAY):
            logging.debug(f"GPIO pin {GPIO_PIN_AUTO_SHUTDOWN} is LOW for {AUTO_OFF_DELAY} seconds. Shutting down the host...")
            time.sleep(1)  # Pause to allow logging to write to buffer
            shutdown_host()
            return

        # Check for delayed shutdown for GPIO_PIN_MANUAL_SHUTDOWN (when pin goes high)
        if current_state_manual == 1:
            if high_start_time_manual is None:
                high_start_time_manual = time.time()
        else:
            high_start_time_manual = None

        if high_start_time_manual and (time.time() - high_start_time_manual >= MANUAL_OFF_DELAY):
            logging.debug(f"GPIO pin {GPIO_PIN_MANUAL_SHUTDOWN} is HIGH for {MANUAL_OFF_DELAY} seconds. Shutting down the host...")
            time.sleep(1)  # Pause to allow logging to write to buffer
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
