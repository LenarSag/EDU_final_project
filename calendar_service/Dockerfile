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
COPY ./calendar_service /app/calendar_service

# Expose service port
EXPOSE 8002

# Run the service
CMD ["uvicorn", "calendar_service.calendar_main:app", "--host", "0.0.0.0", "--port", "8002"]
