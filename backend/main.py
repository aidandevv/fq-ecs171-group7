from fastapi import FastAPI
from pydantic import BaseModel
import tensorflow as tf
import spacy
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os

def preprocess_text(text, nlp):
    if pd.isna(text):
        return ""
    doc = nlp(str(text).lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model_path = os.path.join('saved_model', 'lyrics_model.keras')
try:
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

try:
    nlp = spacy.load('en_core_web_sm')
    print("Spacy model loaded.")
except OSError:
    print('Spacy model not found. Please run `python -m spacy download en_core_web_sm`')
    nlp = None

class LyricsRequest(BaseModel):
    lyrics: str
    model_name: str

@app.post("/predict")
async def predict(request: LyricsRequest):
    if model is None or nlp is None:
        return {"error": "Model or NLP resources not available."}

    cleaned_lyrics = preprocess_text(request.lyrics, nlp)

    input_data = tf.constant([cleaned_lyrics], dtype=tf.string)
    prediction_proba = model.predict(input_data)[0][0]
    
    threshold = 0.6
    
    classification = "Age Appropriate" if prediction_proba > threshold else "Potentially Explicit"
    
    return {
        "prediction": classification,
        "confidence": float(prediction_proba),
        "score": float(prediction_proba),
        "model": request.model_name
    }

@app.get("/")
def read_root():
    return {"message": "Lyric Classifier API is running."}