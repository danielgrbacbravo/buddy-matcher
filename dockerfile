# Start with a base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy your script and requirements
COPY requirements.txt ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your Python script
CMD ["python", "src/main.py"]
