# Use Ubuntu as base image for better compatibility
FROM ubuntu:24.04

# Avoid timezone prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

# Install system dependencies for OpenCV, Tesseract, and image processing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    tesseract-ocr \
    tesseract-ocr-por \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libtesseract-dev \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies in the virtual environment
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Set Tesseract data path
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Command to run the script using the virtual environment's Python
ENTRYPOINT ["/opt/venv/bin/python3", "ocr.py"]

# Default help command (can be overridden)
CMD ["--help"]
