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

# Copy start.sh
COPY ../../start.sh /app/start.sh

# Copy alembic 
COPY ../../alembic /app/alembic
COPY ../../alembic.ini /app/alembic.ini

# Copy service-specific files
COPY ./auth_service /app/auth_service

# Expose service port
EXPOSE 8001


# Run the service
CMD ["uvicorn", "auth_service.auth_main:app", "--host", "0.0.0.0", "--port", "8001"]


