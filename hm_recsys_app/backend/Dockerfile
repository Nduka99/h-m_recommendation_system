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

# Copy all local files (includes artifacts/ now)
COPY . .

# Expose port
EXPOSE 8000

# Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
