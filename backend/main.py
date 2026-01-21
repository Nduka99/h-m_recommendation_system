import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

from inference import RecSysEngine

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Allow overriding the artifact path via Environment Variable (good for Docker)
# In Docker (WORKDIR /app), artifacts are at /app/artifacts.
# Locally (hm_recsys_app/backend), they are at ./artifacts.
ARTIFACT_DIR = os.getenv("ARTIFACT_DIR", "artifacts") 
# Note: In Docker, we might map artifacts to /app/artifacts, so default might need adjusting based on deployment.
# For local testing from 'hm_recsys_app/backend', '../artifacts' is correct.

# --- Global Components ---
rec_engine = None

class RecommendationRequest(BaseModel):
    customer_id: int
    top_k: int = 12

class RecommendationResponse(BaseModel):
    customer_id: int
    recommendations: List[str]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the model on startup.
    """
    global rec_engine
    logger.info("Server Starting: Loading Recommendation Engine...")
    try:
        # Check if we are in Docker (standard path usually /app/artifacts or similar) or local
        # If running from backend dir locally, artifacts are at ../artifacts
        path_to_use = ARTIFACT_DIR
        
        # Fallback check for local debugging if env var not set and default fails
        if not os.path.exists(path_to_use) and os.path.exists("artifacts"):
             path_to_use = "artifacts"
        
        logger.info(f"Loading artifacts from: {os.path.abspath(path_to_use)}")
        rec_engine = RecSysEngine(artifact_dir=path_to_use)
        logger.info("Recommendation Engine Loaded Successfully.")
    except Exception as e:
        logger.error(f"Failed to load Recommendation Engine: {e}")
        raise e
    
    yield
    
    # Clean up (if needed)
    rec_engine = None
    logger.info("Server Shutting Down.")

# --- API Definition ---
app = FastAPI(title="H&M RecSys API", version="1.0", lifespan=lifespan)

@app.get("/")
def health_check():
    """Health check endpoint for cloud orchestration."""
    if rec_engine is None:
        return {"status": "starting", "model_loaded": False}
    return {"status": "alive", "model_loaded": True}

@app.post("/predict", response_model=RecommendationResponse)
def predict(request: RecommendationRequest):
    """
    Generate recommendations for a given user.
    """
    if rec_engine is None:
        raise HTTPException(status_code=503, detail="Model not yet loaded.")
    
    try:
        logger.info(f"Received request for User {request.customer_id}")
        recs = rec_engine.recommend(request.customer_id, top_k=request.top_k)
        return {
            "customer_id": request.customer_id,
            "recommendations": recs
        }
    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Allow running directly for debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
