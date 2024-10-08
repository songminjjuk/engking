import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../assets/css/result.css'; // Import the CSS file

const ResultPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { feedback, score, endQuestion, audioFileUrl, title, difficulty } = location.state || {};
    const feedbackSentences = feedback.split(/(?<=[.:!?])\s+/);
    console.log(feedback);

    const feedbackItems = feedback.split(/\n/).map((item, index) => {
        return (
            <div key={index} className="feedback-item">
                {/* Convert line breaks within each feedback item to <br /> elements */}
                {item.split(/(?=\d+\.\s)/).map((line, idx) => {
                    const isNumber = /^\d+\.\s/.test(line); // Check if the line starts with a number
                    return (
                        <span key={idx}>
                            {isNumber && (
                                <>
                                    {/* Add a dividing line above numbered sentences */}
                                    <hr className="conv-divider" />
                                </>
                            )}
                            {/* Bold numbered sentences */}
                            {line.trim()}
                            <br />
                        </span>
                    );
                })}
            </div>
        );
    });
    return (
        <div className="result-container">
            <div className="result-section"> 
            <div className="res_title">회화 연습 결과</div>
            <p><strong>주제:</strong> {title}</p>
            <p><strong>난이도:</strong> {difficulty}</p>
            <p><strong>점수:</strong> {score}</p>
            <p><strong>피드백:</strong></p>
            <div className="feedback-section">
                    {feedbackItems}
                </div>
            
            <p><strong>{endQuestion}</strong></p>
            {/* {audioFileUrl && (
                <div className="audio-player-container">
                    <h3>Your Recording:</h3>
                    <audio controls src={audioFileUrl}></audio>
                </div>
            )} */}

            <button className="back-button" onClick={() => navigate(-1)}>
                Back to Conversation
            </button>
            </div>
        </div>
    );
};

export default ResultPage;
