import csv
import os
import random

random.seed(42)

# Number of deliberately invalid rows in each shard.
INVALID_COUNTS = [1, 2, 0, 3, 1, 2, 0, 2]

os.makedirs("shards", exist_ok=True)

for shard_id, invalid_count in enumerate(INVALID_COUNTS):
    rows = []

    # 20 rows per shard
    for i in range(20):
        user_id = shard_id * 20 + i + 1
        name = f"User{user_id}"
        email = f"user{user_id}@example.com"

        rows.append([user_id, name, email])

    # Replace the first `invalid_count` rows with deliberately invalid data.
    for i in range(invalid_count):
        if i % 2 == 0:
            # Missing email
            rows[i][2] = ""
        else:
            # Malformed email
            rows[i][2] = "invalid-email"

    filename = f"shards/shard-{shard_id}.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "name", "email"])
        writer.writerows(rows)

    print(
        f"{filename}: 20 rows, "
        f"{invalid_count} deliberately invalid rows"
    )
