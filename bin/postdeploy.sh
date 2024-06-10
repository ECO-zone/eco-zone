#!/bin/bash

# This script ensures that the app is ready to run.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Notify Sentry of the new release
curl $SENTRY_RELEASE_URL \
  -X POST \
  -H 'Content-Type: application/json' \
  -d "{\"version\": \"${GIT_REV}\"}"
