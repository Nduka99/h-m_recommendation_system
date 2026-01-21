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

# Copy Artifacts (Explicitly to exclude heavy 500MB index)
# We assume these exist in backend/artifacts/ from the setup step
COPY artifacts/features_user.parquet artifacts/
COPY artifacts/features_item.parquet artifacts/
COPY artifacts/candidates_pool.parquet artifacts/
COPY artifacts/article_map.parquet artifacts/
COPY artifacts/lgbm_ranker.txt artifacts/

# DEBUG: List the artifacts directory to confirm files are present during build
RUN ls -la artifacts/

# Expose port
EXPOSE 8000

# Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
