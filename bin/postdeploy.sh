#!/bin/bash

# This script ensures that the app is ready to run.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Notify Sentry of the new release
wget --header="Content-Type: application/json" \
  --post-data="{\"version\": \"${GIT_REV}\"}" \
  --output-document - \
  $SENTRY_RELEASE_URL
