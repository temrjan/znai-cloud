#!/bin/bash
cd /home/temrjan/znai-cloud
source venv/bin/activate
export $(grep -v '^#' .env | xargs)
/home/temrjan/znai-cloud/venv/bin/celery -A backend.app.celery_app worker --loglevel=info --concurrency=2 -Q documents,celery
