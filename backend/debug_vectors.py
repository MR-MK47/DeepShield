
import logging
from services.osint_search import search_deepfake_candidates
from services.face_engine import extract_face_vector
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug")

# 1. Get reference
ref_url = "https://universaljacket.com/wp-content/uploads/2023/04/3.jpg"
vec_ref = extract_face_vector(requests.get(ref_url).content)
print(f"Ref vector (ArcFace): {vec_ref[:5]}")

# 2. Search
from services.osint_search import _build_search_terms
terms = _build_search_terms("Puffer Jacket Pope")
print(f"Terms: {terms}")

# 3. Simulate part of search
from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.images(terms[0], max_results=5))
    for r in results:
        url = r.get("image")
        print(f"Checking URL: {url}")
        try:
            vec_cand = extract_face_vector(requests.get(url, timeout=5).content)
            # Check if ArcFace or pHash
            from services.face_engine import compute_similarity
            sim = compute_similarity(vec_ref, vec_cand)
            print(f"  Similarity: {sim}")
        except Exception as e:
            print(f"  Failed: {e}")
