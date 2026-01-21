# Start from python slim
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy from Repo Root: hm_recsys_app/backend/requirements.txt
COPY hm_recsys_app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY hm_recsys_app/backend/ .

# Copy artifacts from repo root
COPY artifacts/ /artifacts

# Expose port
EXPOSE 8000

# Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
