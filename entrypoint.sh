#!/bin/sh

# Only create directories if they don't already exist
[ ! -d "/input" ] && mkdir -p /input
[ ! -d "/output" ] && mkdir -p /output
[ ! -d "/config" ] && mkdir -p /config

# Check if /default-config has files to copy
if [ -d "/default-config" ] && [ "$(ls -A /default-config)" ]; then
  # Copy each default config file if it does not already exist in /config
  for file in /default-config/*; do
    filename=$(basename "$file")
    if [ ! -f "/config/$filename" ]; then
      echo "Copying default config file $filename to /config"
      cp "$file" "/config/$filename"
    fi
  done
else
  echo "No default config files found in /default-config."
fi

# Check if local_students.csv and input.csv exist in /input
[ -f "/input/local_students.csv" ] && [-f "/input/incoming_students.csv" ] && exec python3 src/main.py "$@" || \
echo "local_students.csv and incoming_students.csv must be present in /input \n  run again once they are present." && exit 1
