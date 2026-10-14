
import logging
from services.osint_search import search_deepfake_candidates
from services.face_engine import extract_face_vector
import requests

logging.basicConfig(level=logging.INFO)

# Test query
query = "Puffer Jacket Pope"
# I need a reference vector to search against, but I can just inspect 
# the DDGS results and see if they have faces.

from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.images(query, max_results=5))
    print(f"Search results for '{query}':")
    for i, r in enumerate(results):
        url = r.get("image") or r.get("url") or r.get("image_url")
        print(f"{i}. URL: {url}")
        
        # Test extraction
        try:
            resp = requests.get(url, timeout=5)
            vec = extract_face_vector(resp.content)
            print(f"   Vector extracted: {len(vec) if vec else 'Failed'}")
        except Exception as e:
            print(f"   Failed to process: {e}")
