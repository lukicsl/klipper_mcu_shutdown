# Use a lightweight base image with Python
FROM python:3.9-slim

# Install gnupg and other required packages
RUN apt-get update && apt-get install -y \
    gnupg \
    gcc \
    python3-dev \
    sudo \
    util-linux \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add the Raspberry Pi OS repository to sources.list
RUN echo "deb http://archive.raspberrypi.org/debian/ buster main" > /etc/apt/sources.list.d/raspi.list

# Add the Raspberry Pi OS public key
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E

# Install raspi-gpio
RUN apt-get update && apt-get install -y \
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
