#!/bin/bash

# This script ensures that the app is ready to run.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# For running any Django management commands
RUN_DJANGO_COMMAND='python /app/manage.py'

# Run migrations
echo "Running migrations..."
$RUN_DJANGO_COMMAND migrate

exec "$@"
