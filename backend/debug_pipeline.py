
import logging
from services.osint_search import search_deepfake_candidates
from services.face_engine import extract_face_vector
import requests

logging.basicConfig(level=logging.INFO)

# 1. Get a reference vector (using the Pope image)
ref_url = "https://universaljacket.com/wp-content/uploads/2023/04/3.jpg"
resp = requests.get(ref_url)
ref_vec = extract_face_vector(resp.content)
print(f"Reference vector length: {len(ref_vec)}")

# 2. Run the search
print("Running search_deepfake_candidates...")
matches = search_deepfake_candidates(
    query_vector=ref_vec,
    query_text="Puffer Jacket Pope",
    threshold=0.55 # The current default
)

print(f"Found {len(matches)} matches:")
for c in matches:
    print(f'  - {c["domain"]}: {c["similarity"]}')
