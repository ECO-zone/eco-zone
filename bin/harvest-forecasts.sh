#!/bin/bash

# This script harvests data.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# For running any Django management commands
RUN_DJANGO_COMMAND='python /app/manage.py'

# Harvest forecast data
echo "Harvesting forecast data..."
$RUN_DJANGO_COMMAND harvest aggregate_forecast
$RUN_DJANGO_COMMAND harvest renewable_forecast --forecast_type=day-ahead
$RUN_DJANGO_COMMAND harvest renewable_forecast --forecast_type=intraday
$RUN_DJANGO_COMMAND harvest renewable_forecast --forecast_type=current
$RUN_DJANGO_COMMAND update forecasts
