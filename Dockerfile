# Use the official Ubuntu base image (since it includes more dependencies)
FROM ubuntu:22.04

# Set the working directory in the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libasound2 \
    libportaudio2 \
    libcairo2-dev \
    gobject-introspection \
    gir1.2-gst-plugins-base-1.0 \
    gir1.2-gstreamer-1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    python3-gi \
    python3-gi-cairo \
    python3-gst-1.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip and upgrade it
RUN apt-get update && apt-get install -y python3-pip && pip3 install --upgrade pip

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the command to run your application
CMD ["python3", "main.py"]
