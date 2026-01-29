#!/bin/bash
set -e

echo "=== Startup Debug ===" | tee /home/LogFiles/startup.log
echo "Python: $(which python3)" | tee -a /home/LogFiles/startup.log
echo "Pip packages:" | tee -a /home/LogFiles/startup.log
pip list 2>&1 | tee -a /home/LogFiles/startup.log
echo "Working dir: $(pwd)" | tee -a /home/LogFiles/startup.log
echo "Contents:" | tee -a /home/LogFiles/startup.log
ls -la | tee -a /home/LogFiles/startup.log
echo "=== Starting gunicorn ===" | tee -a /home/LogFiles/startup.log

gunicorn backend.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    2>&1 | tee -a /home/LogFiles/startup.log
