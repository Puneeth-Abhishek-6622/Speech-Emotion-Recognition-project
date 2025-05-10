import axios from "axios";
import React, { useState } from "react";
import "./App.css"; // Import the CSS file

export default function App() {
  const [file, setFile] = useState(null);
  const [emotion, setEmotion] = useState(null);
  const [recommendations, setRecommendations] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setEmotion(null);
    setRecommendations({});
    
    const formData = new FormData();
    formData.append("audio", file);

    try {
      // First, get the emotion prediction
      const response = await axios.post(
        "http://localhost:5000/predict",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setEmotion(response.data.emotion);
      
      // Then, fetch recommendations
      setLoadingRecommendations(true);
      const recommendationsResponse = await axios.post(
        "http://localhost:5000/get_recommendations",
        { emotion: response.data.emotion }
      );
      setRecommendations(recommendationsResponse.data.recommendations);
    } catch (error) {
      console.error("Error processing request", error);
    } finally {
      setLoading(false);
      setLoadingRecommendations(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Emotion based music recommendation system</h1>
        <form
          accept="audio/wav"
          onChange={handleFileChange}
          className="file-upload-form"
        >
          <label htmlFor="file" className="file-upload-label">
            <div className="file-upload-design">
              <svg viewBox="0 0 640 512" height="1em">
                <path d="M144 480C64.5 480 0 415.5 0 336c0-62.8 40.2-116.2 96.2-135.9c-.1-2.7-.2-5.4-.2-8.1c0-88.4 71.6-160 160-160c59.3 0 111 32.2 138.7 80.2C409.9 102 428.3 96 448 96c53 0 96 43 96 96c0 12.2-2.3 23.8-6.4 34.6C596 238.4 640 290.1 640 352c0 70.7-57.3 128-128 128H144zm79-217c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l39-39V392c0 13.3 10.7 24 24 24s24-10.7 24-24V257.9l39 39c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-80-80c-9.4-9.4-24.6-9.4-33.9 0l-80 80z"></path>
              </svg>
              <p>Drag and Drop</p>
              <p>or</p>
              <span className="browse-button">Browse file</span>
            </div>
            <input id="file" type="file" />
          </label>
        </form>

        {loading && (
          <div className="loading">
            <p>Analyzing audio...</p>
          </div>
        )}

        {emotion && (
          <div className="card1">
            <div className="card-info">
              <h2>Predicted Emotion: {emotion}</h2>

              {loadingRecommendations && (
                <div className="loading">
                  <p>Fetching recommendations...</p>
                </div>
              )}

              {!loadingRecommendations && recommendations.music && (
                <div className="recommendation">
                  <h3>🎵 Music Recommendation</h3>
                  <img
                    src={recommendations.music.thumbnail}
                    alt={recommendations.music.title}
                  />
                  <p>
                    <a
                      href={recommendations.music.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {recommendations.music.title}
                    </a>
                  </p>
                </div>
              )}

              {!loadingRecommendations && recommendations.movie && (
                <div className="recommendation">
                  <h3>🎬 Movie Recommendation</h3>
                  <img
                    src={recommendations.movie.thumbnail}
                    alt={recommendations.movie.title}
                  />
                  <p>
                    <a
                      href={recommendations.movie.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {recommendations.movie.title}
                    </a>
                  </p>
                </div>
              )}

              {!loadingRecommendations && recommendations.book && (
                <div className="recommendation">
                  <h3>📖 Book Recommendation</h3>
                  <img
                    src={recommendations.book.thumbnail}
                    alt={recommendations.book.title}
                  />
                  <p>
                    <a
                      href={recommendations.book.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {recommendations.book.title}
                    </a>
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <button onClick={handleUpload} className="button" disabled={loading}>
        <div className="wrap">
          <p>
            <span>✧</span>
            <span>✦</span>
            {loading ? "Processing..." : "Upload & Analyze"}
          </p>
        </div>
      </button>
    </div>
  );
}
