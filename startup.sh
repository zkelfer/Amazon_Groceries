#!/bin/bash
exec gunicorn backend.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /home/LogFiles/gunicorn-access.log \
    --error-logfile /home/LogFiles/gunicorn-error.log \
    --log-level debug
