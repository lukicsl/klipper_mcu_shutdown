# Use a lightweight base image with Python
FROM python:3.9-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    python3-rpi.gpio \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python script into the container
COPY mcu_shutdown.py /usr/src/app/mcu_shutdown.py

# Set the working directory
WORKDIR /usr/src/app

# Run the Python script
CMD ["python", "mcu_shutdown.py"]
