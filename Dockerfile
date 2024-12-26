# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on (optional, replace with the correct port)
EXPOSE 8000

# Define the command to run your application
CMD ["python", "server.py"]
