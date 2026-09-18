# AI-Ops Assignment 2 


## Repository Structure

```text
AI-Ops-Assignment2/
│
├── generate_data.py              # Generates the deterministic 1,000-message dataset
├── spam_dataset.csv              # Synthetic spam/ham dataset
├── train_model.py                # Trains TF-IDF + MultinomialNB and saves the model
├── model.joblib                  # Saved trained ML pipeline
├── app.py                        # REST API used for Docker Compose (Q2)
├── app_q4.py                     # REST API version used for Kubernetes Deployment (Q4)
├── requirements.txt              # Python dependencies
│
├── generate_shards.py            # Generates 8 deterministic CSV validation shards
├── validator.py                  # Validates one shard using the Indexed Job index
├── shards/
│   ├── shard-0.csv
│   ├── shard-1.csv
│   ├── shard-2.csv
│   ├── shard-3.csv
│   ├── shard-4.csv
│   ├── shard-5.csv
│   ├── shard-6.csv
│   └── shard-7.csv
│
├── screenshots/                  # Folder containing all evidences
│
├── AI_Ops_Assignment2.pdf        # report
│
├── benchmark.py                  # Measures Redis cache miss vs hit latency
│
├── Dockerfile.single              # Q1 naive single-stage Docker build
├── Dockerfile.multi               # Q1/Q2 multi-stage Docker build
├── Dockerfile.validator           # Q3 validator image
├── Dockerfile.q4                  # Q4 Kubernetes API image
│
├── docker-compose.yml             # Q2 API + Redis multi-container stack
│
└── k8s/
    ├── indexed-job.yaml           # Q3 Kubernetes Indexed Job
    ├── deployment.yaml             # Q4 Kubernetes Deployment
    └── service.yaml                # Q4 Kubernetes Service
```

## API Endpoints

### `GET /healthz`

Returns a successful response when the API and model are loaded.

Example:

```json
{"status":"ok"}
```

In Q4, the endpoint also exposes the API version:

```json
{"status":"ok","version":"v1"}
```

### `POST /predict`

Accepts a text message and returns its predicted label.

Request:

```json
{"text":"WIN a FREE iPhone now!"}
```

Response:

```json
{"label":"spam"}
```

## Question 1 — Docker Single-Stage vs Multi-Stage

The API was packaged using two Dockerfiles.

- `Dockerfile.single` uses the larger `python:3.11` image as a single runtime/build environment.
- `Dockerfile.multi` uses `python:3.11` as a builder and `python:3.11-slim` as the final runtime image.
- The final multi-stage image copies only the installed dependencies and required application files from the builder.

Measured content sizes:

```text
Single-stage: 502 MB
Multi-stage:  137 MB
Reduction:    72.71%
```

## Question 2 — Docker Compose + Redis

`docker-compose.yml` defines two services:

```text
api    → Spam-detection FastAPI service
cache  → Redis 7 Alpine cache
```

The API connects to Redis using the Compose service name `cache` as the hostname.

The cache logic is:

```text
Request
  ↓
Check Redis
  ├── HIT  → return cached label
  └── MISS → run ML model → store result → return label
```

The cache TTL is **300 seconds**.

Measured benchmark:

```text
Cache miss: 18.987 ms
Cache hit:   1.178 ms
Speedup:      16.12x
Reduction:    93.80%
```

## Question 3 — Kubernetes Indexed Job

A separate batch workload validates eight CSV shards containing user signup records.

`generate_shards.py` creates the eight deterministic shards, while `validator.py` validates exactly one shard per Indexed Job completion.

The Job uses:

```yaml
completions: 8
parallelism: 4
completionMode: Indexed
```

Each pod requests and limits **1 CPU**. The completion index is obtained through the Kubernetes Downward API and maps directly to:

```text
completion index i → /app/shards/shard-i.csv
```

The pod also receives its pod name and node name through the Downward API, allowing the logs to identify which pod and node processed each shard.

## Question 4 — Kubernetes Deployment

The spam-detection API is deployed using:

- **2 replicas**
- CPU requests/limits
- a readiness probe on `/healthz`
- a NodePort Service
- a rolling-update strategy

The Deployment demonstrates two Kubernetes behaviors:

### Self-healing

Deleting one running API pod causes the ReplicaSet managed by the Deployment to automatically create a replacement pod and restore the desired replica count of two.

### Rolling update

The API health response was changed from version `v1` to `v2`. A new image tag was built and the Deployment was updated to use it.

The rollout was verified with:

```bash
kubectl rollout status deployment/spam-api
kubectl rollout history deployment/spam-api
```

The final API returned:

```json
{"status":"ok","version":"v2"}
```

## Running the Project

### Generate the spam dataset

```bash
python3 generate_data.py
```

### Train the model

```bash
python3 train_model.py
```

### Run the API locally

```bash
uvicorn app:app --host 0.0.0.0 --port 8001
```

### Run Docker Compose

```bash
docker compose up --build
```

The API is exposed on host port `8001` and Redis is available internally as `cache:6379`.

### Kubernetes Indexed Job

Load the validator image into Minikube:

```bash
minikube image load spam-shard-validator:latest
```

Apply the Indexed Job:

```bash
kubectl apply -f k8s/indexed-job.yaml
```

Check pods:

```bash
kubectl get pods -o wide
```

Collect logs:

```bash
kubectl logs -l app=shard-validator --prefix
```

### Kubernetes Deployment

Load the API image:

```bash
minikube image load spam-api-q4:v1
```

Apply the Deployment and Service:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check status:

```bash
kubectl get deployments
kubectl get pods -l app=spam-api -o wide
kubectl get service spam-api-service
```

Access the API through the Minikube NodePort:

```bash
curl http://$(minikube ip):30080/healthz
```

