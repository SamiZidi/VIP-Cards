# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev gcc && \
    pip install --no-cache-dir -r requirements.txt


# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Copy entrypoint script
COPY build.sh /build.sh
RUN chmod +x /build.sh

# Run entrypoint
ENTRYPOINT ["/build.sh"]
