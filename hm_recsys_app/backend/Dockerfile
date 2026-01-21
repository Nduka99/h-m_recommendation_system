# Start from python slim
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy local requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all local files
COPY . .

# Be explicit about artifacts to ensure they are captured even if context is weird
COPY artifacts/ artifacts/

# DEBUG: List the artifacts directory to confirm files are present during build
RUN ls -la artifacts/

# Expose port
EXPOSE 8000

# Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
