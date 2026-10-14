
import logging
import requests
import io
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_pipeline")

BASE_URL = "http://localhost:8000"

def run_debug():
    # 1. Analyze
    ref_url = "https://universaljacket.com/wp-content/uploads/2023/04/3.jpg"
    img_resp = requests.get(ref_url)
    
    files = {"file": ("pope.jpg", io.BytesIO(img_resp.content), "image/jpeg")}
    r1 = requests.post(f"{BASE_URL}/api/analyze", files=files)
    
    if r1.status_code != 200:
        print(f"Analyze failed: {r1.text}")
        return
        
    data = r1.json()
    vector = data["vector"]
    print(f"Analyzed vector dim: {len(vector)}")
    
    # 2. Search
    payload = {
        "vector": vector,
        "query_text": "Puffer Jacket Pope",
        "threshold": 0.55
    }
    r2 = requests.post(f"{BASE_URL}/api/search", json=payload)
    
    if r2.status_code != 200:
        print(f"Search failed: {r2.text}")
        return
        
    matches = r2.json()
    print(f"Matches found: {len(matches)}")
    for m in matches:
        print(f"  Match: {m['domain']} - Similarity: {m['similarity']}")

if __name__ == "__main__":
    run_debug()
