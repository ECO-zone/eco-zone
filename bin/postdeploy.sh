#!/bin/bash

# This script ensures that the app is ready to run.

# Set path
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Notify Sentry of the new release
curl https://us.sentry.io/api/hooks/release/builtin/4507407118893056/88770a9376df40d110be8845180139f9f28b707df7672136841e7406f26b9090/ \
  -X POST \
  -H 'Content-Type: application/json' \
  -d {\"version\": \"${GIT_REV}\"}"
