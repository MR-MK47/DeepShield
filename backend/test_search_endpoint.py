"""
Test the search endpoint to see what data is actually being returned
"""
import requests
import io
from PIL import Image

print("=" * 70)
print("TESTING SEARCH ENDPOINT - CHECKING RETURNED DATA")
print("=" * 70)

# Create a test image
img = Image.new('RGB', (200, 200), color=(100, 150, 200))
buf = io.BytesIO()
img.save(buf, format='PNG')
buf.seek(0)

# 1. Analyze the image
print("\n1. Calling /api/analyze...")
files = {'file': ('test.png', buf, 'image/png')}
analyze_resp = requests.post('http://localhost:8000/api/analyze', files=files)

if analyze_resp.status_code != 200:
    print(f"ERROR: {analyze_resp.status_code} - {analyze_resp.text}")
    exit(1)

analyze_data = analyze_resp.json()
print(f"   Status: {analyze_data['status']}")
print(f"   Vector length: {len(analyze_data['vector'])}")
print(f"   Hash: {analyze_data['hash']}")

# 2. Search with the vector
print("\n2. Calling /api/search with threshold 0.30...")
search_payload = {
    'vector': analyze_data['vector'],
    'query_text': 'Puffer Jacket Pope',
    'threshold': 0.30
}

search_resp = requests.post('http://localhost:8000/api/search', json=search_payload)

if search_resp.status_code != 200:
    print(f"ERROR: {search_resp.status_code} - {search_resp.text}")
    exit(1)

matches = search_resp.json()
print(f"   Status: {search_resp.status_code}")
print(f"   Matches returned: {len(matches)}")

if matches:
    print("\n3. Match structure:")
    for i, m in enumerate(matches[:3], 1):
        print(f"\n   Match {i}:")
        print(f"     url: {m.get('url', 'MISSING')[:60]}...")
        print(f"     domain: {m.get('domain', 'MISSING')}")
        print(f"     similarity: {m.get('similarity', 'MISSING')}")
        print(f"     thumbnail: {m.get('thumbnail', 'MISSING')[:60]}...")
else:
    print("\n   WARNING: No matches in response!")
    print(f"   Response text: {search_resp.text[:500]}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
