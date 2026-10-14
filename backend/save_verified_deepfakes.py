
import requests
import io
import os
import logging
from services.face_engine import extract_face_vector
from ddgs import DDGS

logging.basicConfig(level=logging.INFO)
TARGET_DIR = r"C:\Users\mkazi\OneDrive\Desktop\Deepfakes"
os.makedirs(TARGET_DIR, exist_ok=True)

queries = ["Pope Francis puffer jacket", "Elon Musk face swap"]
processed_count = 0

for query in queries:
    print(f"Searching for: {query}")
    with DDGS() as ddgs:
        results = list(ddgs.images(query, max_results=5))
        for r in results:
            url = r.get("image")
            if not url: continue
            
            try:
                print(f"Testing: {url}")
                resp = requests.get(url, timeout=5)
                # Verify face
                vec = extract_face_vector(resp.content)
                if vec:
                    # Save if valid
                    filename = os.path.join(TARGET_DIR, f"{query.replace(' ', '_')}_{processed_count}.jpg")
                    with open(filename, "wb") as f:
                        f.write(resp.content)
                    print(f"Saved: {filename}")
                    processed_count += 1
                    if processed_count >= 5: break
            except Exception as e:
                print(f"Failed to process: {e}")
