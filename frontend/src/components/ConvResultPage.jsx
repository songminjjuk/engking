import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../assets/css/result.css'; // Import the CSS file

const ResultPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { feedback, score, endQuestion, audioFileUrl, title, difficulty } = location.state || {};

    return (
        <div className="result-container">
            <div className="res_title">회화 연습 결과</div>
            <p><strong>주제:</strong> {title}</p>
            <p><strong>난이도:</strong> {difficulty}</p>
            <p><strong>피드백:</strong>{feedback}</p>
            <p><strong>점수:</strong> {score}</p>
            <p><strong>{endQuestion}</strong></p>
            {audioFileUrl && (
                <div className="audio-player-container">
                    <h3>Your Recording:</h3>
                    <audio controls src={audioFileUrl}></audio>
                </div>
            )}

            <button className="back-button" onClick={() => navigate(-1)}>
                Back to Conversation
            </button>
        </div>
    );
};

export default ResultPage;
