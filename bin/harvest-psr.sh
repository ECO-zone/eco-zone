#!/bin/bash

# This script harvests data.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# For running any Django management commands
RUN_DJANGO_COMMAND='python /app/manage.py'

# Harvest redispatch data
echo "Harvesting redispatch data..."
$RUN_DJANGO_COMMAND harvest psr
