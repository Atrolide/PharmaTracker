# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the src into the container at /app/src
COPY /src /app/src

# Install any needed packages specified in src/requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run uvicorn server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
