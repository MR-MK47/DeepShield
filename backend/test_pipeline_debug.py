"""
End-to-End Pipeline Test - Debugging Search Results
Tests each phase: Analyze -> Search -> Match Display
"""

import io
import logging
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from main import app

client = TestClient(app)

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (200, 200), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

print("=" * 70)
print("PHASE 1: Testing /api/analyze endpoint")
print("=" * 70)

# Test analyze
img_bytes = create_test_image()
response = client.post(
    "/api/analyze",
    files={"file": ("test.png", img_bytes, "image/png")}
)

print(f"Status Code: {response.status_code}")
if response.status_code != 200:
    print(f"ERROR Response: {response.text}")
    exit(1)

analyze_data = response.json()
print(f"[OK] Status: {analyze_data['status']}")
print(f"[OK] Vector length: {len(analyze_data['vector'])}")
print(f"[OK] Hash: {analyze_data['hash']}")
print(f"[OK] Vector sample (first 5): {analyze_data['vector'][:5]}")

# Check if vector is actually populated or all zeros
vec_np = np.array(analyze_data['vector'])
vec_norm = np.linalg.norm(vec_np)
print(f"[OK] Vector L2 norm: {vec_norm:.6f}")

if vec_norm < 0.1:
    print("[WARN] Vector is nearly zero - may be pHash fallback")
else:
    print("[OK] Vector has meaningful values")

print("\n" + "=" * 70)
print("PHASE 2: Testing /api/search endpoint")
print("=" * 70)

# Test search with the vector from analyze
search_payload = {
    "vector": analyze_data['vector'],
    "query_text": "Puffer Jacket Pope",
    "threshold": 0.55
}

print(f"Search payload: vector_len={len(search_payload['vector'])}, query='{search_payload['query_text']}', threshold={search_payload['threshold']}")

response = client.post(
    "/api/search",
    json=search_payload
)

print(f"Status Code: {response.status_code}")
if response.status_code != 200:
    print(f"ERROR Response: {response.text}")
    exit(1)

matches = response.json()
print(f"[OK] Matches found: {len(matches)}")

if len(matches) > 0:
    print("\nMatch details:")
    for i, m in enumerate(matches, 1):
        print(f"  {i}. Domain: {m['domain']}")
        print(f"     URL: {m['url'][:60]}...")
        print(f"     Similarity: {m['similarity']:.4f} ({m['similarity']*100:.1f}%)")
else:
    print("[WARN] No matches returned!")
    print("\nInvestigating why no matches...")
    
    # Check if the issue is with DDGS
    print("\nTesting DDGS directly:")
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images("Puffer Jacket Pope", max_results=5))
            print(f"  DDGS returned {len(results)} results")
            if results:
                for r in results[:3]:
                    print(f"    - {r.get('title', 'No title')[:50]}")
    except Exception as e:
        print(f"  DDGS ERROR: {e}")

print("\n" + "=" * 70)
print("PHASE 3: Testing with lower threshold")
print("=" * 70)

# Try with much lower threshold
search_payload['threshold'] = 0.30
response = client.post("/api/search", json=search_payload)
matches_low = response.json()
print(f"Matches with threshold 0.30: {len(matches_low)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Analyze: {'PASS' if analyze_data['status'] == 'success' else 'FAIL'}")
print(f"Search (0.55): {'PASS' if len(matches) > 0 else 'FAIL - No matches'}")
print(f"Search (0.30): {'PASS' if len(matches_low) > 0 else 'FAIL - No matches'}")
