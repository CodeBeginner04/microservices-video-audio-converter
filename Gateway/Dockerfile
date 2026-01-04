# Use Python 3.10 slim image based on Debian Bullseye
FROM python:3.10-slim-bullseye

# Install system dependencies for MySQL
# - build-essential: C compiler needed for some Python packages
# - default-libmysqlclient-dev: MySQL client library headers
RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --requirement requirements.txt

# Copy application code
COPY . /app

# Expose port 8080 (Flask default)
EXPOSE 8080

# Run the application
CMD ["python", "server.py"]