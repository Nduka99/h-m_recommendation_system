import pandas as pd
import os

# Paths inside Docker container
candidates_path = 'artifacts/candidates_pool.parquet'
# Images not mounted in backend, so we estimate
AVG_IMG_SIZE_MB = 0.15 

# Load candidates
print("Loading candidates...")
df = pd.read_parquet(candidates_path)
count = len(df)
print(f"Total Candidates: {count}")

est_total_size = count * AVG_IMG_SIZE_MB
print(f"--- Estimates ---")
print(f"Estimated Total Size: {est_total_size:.2f} MB")

