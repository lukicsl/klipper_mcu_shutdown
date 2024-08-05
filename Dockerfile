# Use a lightweight base image with Python
FROM python:3.9-slim

# Install required packages and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    sudo \
    util-linux \
    raspi-gpio \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install RPi.GPIO using pip
RUN python3 -m pip install RPi.GPIO

# Copy the Python script into the container
COPY mcu_shutdown.py /usr/src/app/mcu_shutdown.py

# Set the working directory
WORKDIR /usr/src/app

# Set environment variables if needed
ENV LOW_DURATION_THRESHOLD=10

# Run the Python script
CMD ["python3", "mcu_shutdown.py"]
