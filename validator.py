import csv
import os
import re
import time


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

job_index = os.environ["JOB_INDEX"]
pod_name = os.environ["POD_NAME"]
node_name = os.environ["NODE_NAME"]

shard_id = int(job_index)
shard_path = f"/app/shards/shard-{shard_id}.csv"

print(f"Pod: {pod_name}")
print(f"Node: {node_name}")
print(f"Indexed completion: {shard_id}")
print(f"Validating: {shard_path}")

invalid_count = 0

with open(shard_path, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        user_id = row.get("user_id", "").strip()
        name = row.get("name", "").strip()
        email = row.get("email", "").strip()

        if not user_id or not name or not email:
            invalid_count += 1
        elif not EMAIL_PATTERN.match(email):
            invalid_count += 1

print(f"Shard {shard_id}: invalid rows = {invalid_count}")

# Keep the pod alive briefly so concurrent execution is observable.
time.sleep(10)

print(f"Shard {shard_id} validation complete.")
