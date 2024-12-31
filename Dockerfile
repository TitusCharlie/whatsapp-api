# Use the official Python image from Docker Hub
FROM python:3.11-slim
# Set the working directory
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    # && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY . /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# # Copy the project files
# COPY . /app/
# Run migrations
RUN python manage.py migrate

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]