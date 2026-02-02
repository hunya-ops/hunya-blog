#!/bin/bash
set -e

# Fix permissions for data directories
# Docker binds host directories as root, so we need to change ownership to appuser
if [ -d "/app/data" ]; then
    chown -R appuser:appuser /app/data
fi

if [ -d "/app/app/static/uploads" ]; then
    chown -R appuser:appuser /app/app/static/uploads
fi

# Drop privileges and execute the command as appuser
# gosu ensures the process receives signals correctly (unlike su)
exec gosu appuser "$@"
