import sys
import os
import json

# Add backend to sys.path to ensure imports work
sys.path.append(os.path.join(os.getcwd(), 'hm_recsys_app', 'backend'))

# Set Environment Variable BEFORE importing main to ensure it picks it up
os.environ["ARTIFACT_DIR"] = os.path.join("hm_recsys_app", "artifacts")
print(f"Set ARTIFACT_DIR to: {os.environ['ARTIFACT_DIR']}")

try:
    from fastapi.testclient import TestClient
    from main import app
    from inference import RecSysEngine
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_inference_direct():
    print("\n--- Testing RecSysEngine Directly ---")
    try:
        # Assuming we are running from project root, path is same as env var
        artifact_path = os.environ["ARTIFACT_DIR"]
        print(f"Loading artifacts from: {os.path.abspath(artifact_path)}")
        
        engine = RecSysEngine(artifact_dir=artifact_path)
        print("Engine initialized.")
        
        # Test with a dummy user ID
        user_id = 123456
        print(f"Generating recommendations for User {user_id}...")
        recs = engine.recommend(user_id, top_k=5)
        print(f"Recommendations: {recs}")
        
        if not recs:
            print("WARNING: No recommendations returned (Empty list).")
        else:
            print("SUCCESS: Recommendations generated.")
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

def test_fastapi_endpoint():
    print("\n--- Testing FastAPI Endpoint ---")
    try:
        with TestClient(app) as client:
            # 1. Health Check
            response = client.get("/")
            print(f"Health Check: {response.status_code} - {response.json()}")
            assert response.status_code == 200
            
            # 2. Predict
            payload = {"customer_id": 123456, "top_k": 5}
            print(f"Sending Predict Request: {payload}")
            response = client.post("/predict", json=payload)
            print(f"Response: {response.status_code}")
            print(f"Body: {response.json()}")
            
            if response.status_code == 200:
                print("SUCCESS: API responded correctly.")
            else:
                print("FAILED: API Error.")
                
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Verification...")
    test_inference_direct()
    test_fastapi_endpoint()
