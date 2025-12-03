# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for Playwright and general tools
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Copy the rest of the application code
COPY . .

# Expose the port (if we decide to run via HTTP/SSE later, though MCP is stdio by default)
# EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "src/meganx_mcp_server.py"]
