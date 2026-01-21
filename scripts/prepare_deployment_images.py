import pandas as pd
import os
from PIL import Image
import shutil

# Config
CANDIDATES_PATH = "/app/artifacts/candidates_pool.parquet"
MAPPING_PATH = "/app/artifacts/article_map.parquet"
SOURCE_IMAGES_DIR = "/data/images"
OUTPUT_DIR = "/output"
TARGET_SIZE = (400, 600)  # Width, Height (Approx generic portrait)
JPEG_QUALITY = 80

def optimize_assets():
    print("--- Starting Asset Optimization ---", flush=True)
    
    # Log file
    log_path = os.path.join(OUTPUT_DIR, "debug_log.txt")
    print(f"Logging to {log_path}", flush=True)
    
    with open(log_path, "w") as f:
        f.write("--- Asset Optimization Log ---\n")
        
        # Check source
        if not os.path.exists(SOURCE_IMAGES_DIR):
             f.write(f"CRITICAL: Source dir {SOURCE_IMAGES_DIR} does not exist!\n")
             return
        else:
             try:
                 contents = os.listdir(SOURCE_IMAGES_DIR)[:5]
                 f.write(f"Source dir {SOURCE_IMAGES_DIR} checked. Contents: {contents}\n")
             except Exception as e:
                 f.write(f"Error listing source: {e}\n")

        # 1. Load Candidates & Mapping
        if not os.path.exists(CANDIDATES_PATH) or not os.path.exists(MAPPING_PATH):
            f.write(f"ERROR: Candidates or Mapping not found.\n")
            return

        f.write(f"Loading candidates from {CANDIDATES_PATH}...\n")
        try:
            # Load candidates
            c_df = pd.read_parquet(CANDIDATES_PATH)
            # Load mapping
            m_df = pd.read_parquet(MAPPING_PATH)
            
            # Map IDs
            # Filter mapping to only those in candidates
            candidates_int = c_df['article_id_int'].unique()
            mapped_df = m_df[m_df['article_id_int'].isin(candidates_int)]
            
            item_ids = mapped_df['article_id_str'].astype(str).tolist()
            
            f.write(f"Found {len(item_ids)} unique items in candidate pool (mapped).\n")
        except Exception as e:
             f.write(f"Error reading/mapping parquet: {e}\n")
             return

        # ... Processing ...
        f.write(f"Processing images from {SOURCE_IMAGES_DIR} to {OUTPUT_DIR}...\n")
        
        success_count = 0
        missing_count = 0
        error_count = 0

        for idx, id_str in enumerate(item_ids):
            # ID Handling
            # String IDs from map might be "0554598001" (10 chars)
            if len(id_str) == 9:
                id_str = "0" + id_str
                
            folder = id_str[:3]
            src_path = os.path.join(SOURCE_IMAGES_DIR, folder, f"{id_str}.jpg")
            dst_folder = os.path.join(OUTPUT_DIR, folder)
            dst_path = os.path.join(dst_folder, f"{id_str}.jpg")

            if idx < 10:
                f.write(f"DEBUG: Checking ID {id_str} -> Path {src_path}\n")
                f.write(f"DEBUG: Exists? {os.path.exists(src_path)}\n")

            if os.path.exists(src_path):
                try:
                    # Create dest folder if needed
                    os.makedirs(dst_folder, exist_ok=True)
                    
                    # Open and Resize
                    with Image.open(src_path) as img:
                        # Convert to RGB (in case of PNG/RGBA) to save as JPEG
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize
                        img.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)
                        
                        # Save optimized
                        img.save(dst_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
                        
                    success_count += 1
                except Exception as e:
                    f.write(f"Failed to process {id_str}: {e}\n")
                    error_count += 1
            else:
                missing_count += 1
                
            if idx % 100 == 0:
                print(f"Progress: {idx}/{len(item_ids)}...", end='\r')

        f.write("\n--- Optimization Complete ---\n")
        f.write(f"Successfully optimized: {success_count}\n")
        f.write(f"Missing source images: {missing_count}\n")
        f.write(f"Errors: {error_count}\n")
        
    print("\nDone.", flush=True)

if __name__ == "__main__":
    optimize_assets()
