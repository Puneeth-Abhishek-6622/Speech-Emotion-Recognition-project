# Speech Emotion Recognition App

A full-stack web application that analyzes speech to detect emotions and provides personalized content recommendations based on the detected emotion.

## Features

- Real-time speech emotion recognition
- Emotion detection for 7 different emotions:
  - Happy
  - Sad
  - Angry
  - Fear
  - Disgust
  - Surprise
  - Neutral
- Personalized content recommendations based on detected emotions:
  - Music recommendations from YouTube
  - Movie suggestions from TMDB
  - Book recommendations from Google Books
- Modern and responsive user interface
- Real-time audio processing

## Tech Stack

### Backend
- Python 3.x
- Flask (Web Framework)
- Wav2Vec2 (Speech Recognition Model)
- Librosa (Audio Processing)
- PyTorch (Deep Learning Framework)
- Flask-CORS (Cross-Origin Resource Sharing)

### Frontend
- React.js
- Axios (HTTP Client)
- React Icons
- TailwindCSS (Styling)
- Modern React Hooks and Components

## Prerequisites

- Python 3.x
- Node.js and npm
- CUDA-capable GPU (optional, for faster inference)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Puneeth-Abhishek-6622/Speech-emotion-detection.git
cd speech-emotion-app
```

2. Backend Setup:
```bash
cd backend
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
pip install -r requirements.txt
```

3. Frontend Setup:
```bash
cd frontend
npm install
```

4. Model Setup:
The Wav2Vec2 model files are not included in the repository due to size limitations. You'll need to:
- Create a directory: `backend/my_wav2vec2_model/`
- Download the model files from Hugging Face or train your own model
- Place the model files in the `backend/my_wav2vec2_model/` directory

## Running the Application

1. Start the Backend Server:
```bash
cd backend
python app.py
```
The backend server will run on `http://localhost:5000`

2. Start the Frontend Development Server:
```bash
cd frontend
npm start
```
The frontend application will run on `http://localhost:3000`

## API Endpoints

### POST /predict
- Accepts audio file
- Returns detected emotion

### POST /get_recommendations
- Accepts emotion as JSON
- Returns personalized recommendations for music, movies, and books

## Project Structure

```
speech-emotion-app/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── uploads/
│   └── my_wav2vec2_model/
└── frontend/
    ├── public/
    ├── src/
    ├── package.json
    └── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Wav2Vec2 model for speech recognition
- YouTube Data API for music recommendations
- TMDB API for movie recommendations
- Google Books API for book recommendations 