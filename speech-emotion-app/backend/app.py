import os
import concurrent.futures
import time
import random
from functools import wraps
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import librosa
import numpy as np
import requests
import torch
import torchaudio
from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor

app = Flask(__name__)
CORS(app)

# Configure requests session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Load model and processor
model_path = "./my_wav2vec2_model"
try:
    print("Loading model...")
    processor = Wav2Vec2Processor.from_pretrained(model_path)
    model = Wav2Vec2ForSequenceClassification.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Free API keys (replace with your own keys if needed)
YOUTUBE_API_KEY = "AIzaSyBxfixA1jQ3RkN0BnKrFDB2GNZIi9ku3HA"
TMDB_API_KEY = "7513363b5ce574ef653ac3e466d64646"
GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q="

# Emotion categories
emotions = ["fear", "angry", "disgust", "neutral", "sad", "surprise", "Happy"]

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        print(f"Failed after {max_retries} attempts: {str(e)}")
                        return None
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def fetch_music(emotion):
    try:
        search_query = f"{emotion} mood music"
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&key={YOUTUBE_API_KEY}&maxResults=5"
        response = session.get(url, timeout=10).json()
        if "items" in response and len(response["items"]) > 0:
            video = random.choice(response["items"])
            return {
                "title": video["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"]
            }
    except Exception as e:
        print(f"Error fetching music: {e}")
        raise  # Re-raise to trigger retry
    return None

@retry_on_failure(max_retries=3)
def fetch_movie(emotion):
    try:
        genre_map = {
            "happy": "35",  # Comedy
            "sad": "18",    # Drama
            "angry": "28",  # Action
            "neutral": "10749",  # Romance
            "fear": "27",   # Horror
            "surprise": "878"  # Sci-Fi
        }
        genre_id = genre_map.get(emotion.lower(), "18")  # Default to Drama
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&page={random.randint(1, 5)}"
        response = session.get(url, timeout=10).json()
        if "results" in response and len(response["results"]) > 0:
            movie = random.choice(response["results"])
            return {
                "title": movie["title"],
                "url": f"https://www.themoviedb.org/movie/{movie['id']}",
                "thumbnail": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
            }
    except Exception as e:
        print(f"Error fetching movie: {e}")
        raise  # Re-raise to trigger retry
    return None

@retry_on_failure(max_retries=3)
def fetch_book(emotion):
    try:
        search_terms = [
            f"{emotion} books",
            f"{emotion} fiction",
            f"{emotion} stories",
            f"{emotion} novels"
        ]
        search_query = random.choice(search_terms)
        url = f"{GOOGLE_BOOKS_API}{search_query}&maxResults=5"
        response = session.get(url, timeout=10).json()
        if "items" in response and len(response["items"]) > 0:
            book = random.choice(response["items"])["volumeInfo"]
            return {
                "title": book["title"],
                "url": book.get("infoLink", "#"),
                "thumbnail": book["imageLinks"]["thumbnail"] if "imageLinks" in book else None
            }
    except Exception as e:
        print(f"Error fetching book: {e}")
        raise  # Re-raise to trigger retry
    return None

def fetch_all_recommendations(emotion):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_music = executor.submit(fetch_music, emotion)
        future_movie = executor.submit(fetch_movie, emotion)
        future_book = executor.submit(fetch_book, emotion)
        
        # Wait for all futures with a timeout
        try:
            music = future_music.result(timeout=15)
            movie = future_movie.result(timeout=15)
            book = future_book.result(timeout=15)
            
            return {
                "music": music,
                "movie": movie,
                "book": book
            }
        except concurrent.futures.TimeoutError:
            print("Timeout while fetching recommendations")
            return {
                "music": future_music.result(timeout=0) if future_music.done() else None,
                "movie": future_movie.result(timeout=0) if future_movie.done() else None,
                "book": future_book.result(timeout=0) if future_book.done() else None
            }

@app.route("/predict", methods=["POST"])
def predict():
    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join("uploads", audio_file.filename)
    audio_file.save(file_path)
    print(f"Processing file: {file_path}")

    # Load and preprocess audio
    try:
        audio, sr = librosa.load(file_path, sr=16000)
        print(f"Audio loaded. Sample rate: {sr}, Shape: {audio.shape}")

        input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values
        input_values = input_values.to(device)

        # Predict emotion
        with torch.no_grad():
            logits = model(input_values).logits
            predicted_id = torch.argmax(logits, dim=-1).item()

        predicted_emotion = emotions[predicted_id] if 0 <= predicted_id < len(emotions) else "Unknown"
        print(f"Predicted Emotion: {predicted_emotion}")

        # Return only the emotion prediction first
        return jsonify({
            "emotion": predicted_emotion,
            "status": "success"
        })

    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get_recommendations", methods=["POST"])
def get_recommendations():
    data = request.get_json()
    emotion = data.get("emotion")
    
    if not emotion:
        return jsonify({"error": "No emotion provided"}), 400

    try:
        recommendations = fetch_all_recommendations(emotion)
        return jsonify({
            "status": "success",
            "recommendations": recommendations
        })
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)