#!/bin/bash
alembic upgrade head


# Start the service
exec uvicorn auth_service.auth_main:app --host 0.0.0.0 --port 8001