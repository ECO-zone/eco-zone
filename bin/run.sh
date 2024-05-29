#!/bin/sh

# This script starts the app and any required services.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

echo "Starting app..."
/usr/local/bin/uwsgi --chdir=/app/ --ini=/app/uwsgi.ini --http-socket=:5000
