from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import redis


"""
This upper commented part is used for question 1 , and lower part is for question 2
"""

#Q1

# app = FastAPI()

# # Load the model when the application starts
# model = joblib.load("model.joblib")


# class Message(BaseModel):
#     text: str


# @app.get("/healthz")
# def healthz():
#     return {"status": "ok"}


# @app.post("/predict")
# def predict(message: Message):
#     prediction = model.predict([message.text])[0]
#     return {"label": prediction}



#Q2

app = FastAPI()

# Load the trained ML model when the application starts
model = joblib.load("model.joblib")

# Redis service hostname will be "cache" in Docker Compose
redis_client = redis.Redis(
    host="cache",
    port=6379,
    decode_responses=True
)

CACHE_TTL = 300  # 5 minutes


class Message(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/predict")
def predict(message: Message):
    text = message.text

    # Check Redis cache using the exact input text as the key
    cached_label = redis_client.get(text)

    if cached_label is not None:
        print(f"CACHE HIT: {text}")
        return {"label": cached_label}

    # Cache miss: perform the actual ML prediction
    prediction = model.predict([text])[0]

    # Store prediction in Redis with TTL
    redis_client.setex(text, CACHE_TTL, prediction)

    print(f"CACHE MISS: {text}")
    return {"label": prediction}
