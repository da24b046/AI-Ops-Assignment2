import time
import urllib.request
import json

url = "http://localhost:8001/predict"
text = "Benchmark message for cache test"

data = json.dumps({"text": text}).encode()
headers = {"Content-Type": "application/json"}

def predict():
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    start = time.perf_counter()

    with urllib.request.urlopen(req) as response:
        response.read()

    return time.perf_counter() - start


miss = predict()
hit = predict()

print(f"Cache miss: {miss*1000:.3f} ms")
print(f"Cache hit : {hit*1000:.3f} ms")
print(f"Speedup   : {miss/hit:.2f}x")
print(f"Reduction : {(miss-hit)/miss*100:.2f}%")
