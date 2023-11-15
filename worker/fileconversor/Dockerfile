# Use an official Python runtime as the base image
FROM python:3.9-slim


RUN apt-get update -y && apt-get install -y \
    ffmpeg \
    libx264-dev \
    libvpx-dev \
    libxvidcore-dev \
    libvorbis-dev

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY worker/fileconversor/ /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable for Flask to run in production mode
ENV ENV=${ENV:-local}
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/cloud-w3-403103-d05bfab17c67.json

COPY ../../.env /app/env/
COPY ../../.env.cloud /app/env/

# Run the Celery worker when the container launches
CMD ["celery", "-A", "app", "worker", "--loglevel=info"]
#CMD ["python", "app.py"]
