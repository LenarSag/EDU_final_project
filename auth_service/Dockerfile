# Use Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy shared requirements from the root directory
COPY ../../requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy shared config + infra
COPY ../../config /app/config
COPY ../../infrastructure /app/infrastructure

# Copy service-specific files
COPY . /app/auth_service

# Copy and make `start.sh` executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose service port
EXPOSE 8001

# Run the start script
ENTRYPOINT ["/start.sh"]