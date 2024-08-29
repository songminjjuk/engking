import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../assets/css/result.css'; // Import the CSS file

const ResultPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { audioUrl, title, difficulty } = location.state || {};

    return (
        <div className="result-container">
            <h2>Conversation Results</h2>
            <p><strong>Title:</strong> {title}</p>
            <p><strong>Difficulty:</strong> {difficulty}</p>

            {audioUrl && (
                <div className="audio-player-container">
                    <h3>Your Recording:</h3>
                    <audio controls src={audioUrl}></audio>
                </div>
            )}

            <button className="back-button" onClick={() => navigate(-1)}>
                Back to Conversation
            </button>
        </div>
    );
};

export default ResultPage;
