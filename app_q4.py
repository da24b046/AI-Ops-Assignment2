from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# Load the trained model at application startup
model = joblib.load("model.joblib")


class Message(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    '''
    first comment is used for initial part
    '''
    
    # return {"status": "ok", "version": "v1"}   
    return {"status": "ok", "version": "v2"}


@app.post("/predict")
def predict(message: Message):
    prediction = model.predict([message.text])[0]
    return {"label": prediction}
