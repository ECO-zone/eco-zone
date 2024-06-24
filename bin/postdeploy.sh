#!/bin/bash

# This script ensures that the app is ready to run.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Notify Sentry of the new release
curl $SENTRY_RELEASE_URL_BACKEND \
  --silent \
  --output /dev/null \
  --show-error \
  --fail \
  -X POST \
  -H 'Content-Type: application/json' \
  -d "{\"version\": \"${GIT_REV}\"}"

curl $SENTRY_RELEASE_URL_FRONTEND \
  --silent \
  --output /dev/null \
  --show-error \
  --fail \
  -X POST \
  -H 'Content-Type: application/json' \
  -d "{\"version\": \"${GIT_REV}\"}"
