# serviceA/Dockerfile

# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 9000 available to the world outside this container
EXPOSE 8080

# Define environment variable for Flask to run in production mode
ENV ENV=cloud

# Define environment variable for Flask to run in production mode
ENV FLASK_ENV=development

# Run app.py when the container launches
CMD ["python", "app.py", "ENV=${ENV}"]
