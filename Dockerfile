# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the application code to the working directory
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir .[dev]


# Run the application
CMD ["pytest"]

