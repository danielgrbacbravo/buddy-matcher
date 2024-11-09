#!/bin/sh

# Check and create the required directories in /data if they don't exist
mkdir -p /input /output /config
exec python3 src/main.py && "$@"
