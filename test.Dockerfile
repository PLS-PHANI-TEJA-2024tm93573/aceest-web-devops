# Dockerfile for running tests with pytest and generating coverage reports
# Use official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent output buffering
ENV PYTHONUNBUFFERED=1


# Set working directory
WORKDIR /app

# Ensure /tmp is writable for SQLite test DB
RUN mkdir -p /tmp && chmod 1777 /tmp

# Install system dependencies (optional but common for CI images)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first for caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run tests when container starts
CMD ["pytest", "--cov=app", "--cov-report=xml", "--cov-report=html", "tests/"]