#!/bin/sh

# Check and create the required directories in /data if they don't exist
mkdir -p /data/input /data/output /data/config
exec python3 src/main.py && "$@"
