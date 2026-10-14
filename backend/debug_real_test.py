
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from services.osint_search import search_deepfake_candidates
from services.face_engine import extract_face_vector
import requests

print("=" * 70)
print("REAL-WORLD TEST: Puffer Jacket Pope")
print("=" * 70)

# Real Pope image reference
ref_url = "https://universaljacket.com/wp-content/uploads/2023/04/3.jpg"
print(f"\n1. Downloading reference: {ref_url}")
resp = requests.get(ref_url, timeout=10)
print(f"   Size: {len(resp.content)} bytes")

print("\n2. Extracting reference vector...")
ref_vec = extract_face_vector(resp.content)
print(f"   Vector dim: {len(ref_vec)}")

print("\n3. Running search with threshold=0.30 (logging all similarities)...")
matches = search_deepfake_candidates(
    query_vector=ref_vec,
    query_text="Puffer Jacket Pope",
    threshold=0.30,
    max_results=20,
)

print(f"\n4. RESULTS: {len(matches)} matches found")
for i, m in enumerate(matches, 1):
    print(f"   {i}. {m['domain']} - {m['similarity']:.4f}")
