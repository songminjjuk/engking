import React from 'react';
import { useLocation } from 'react-router-dom';
import '../assets/css/result.css';

function QuizResultPage() {
    const location = useLocation();
    const { totalQuestions, correctAnswers, score, feedback } = location.state || {
        totalQuestions: 0,
        correctAnswers: 0,
        score: "0.00",
        feedback: "No feedback available."
    };

    // Split feedback into distinct questions based on line breaks
    const feedbackItems = feedback.split(/\n/).map((item, index) => {
        return (
            <div key={index} className="feedback-item" style={{ marginBottom: '5px' }}>
                {/* Convert line breaks within each feedback item to <br /> elements */}
                {item.split(/(?=\d+\.\s)/).map((line, idx) => {
                    const isNumber = /^\d+\.\s/.test(line); // Check if the line starts with a number
                    return (
                        <span key={idx}>
                            {isNumber && (
                                <>
                                    {/* Add a dividing line above numbered sentences */}
                                    <hr className="divider" />
                                </>
                            )}
                            {/* Bold numbered sentences */}
                            {isNumber ? <strong>{line.trim()}</strong> : line.trim()}
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
                <div className="res_title" style={{ textAlign: 'center' }}>퀴즈 결과</div>
                <p><strong>전체 문제 수:</strong> {totalQuestions}</p>
                <p><strong>정답 문제 수:</strong> {correctAnswers}</p>
                <p><strong>점수:</strong> {score}</p>
                <p><strong>결과 분석:</strong></p>
                <div className="feedback-section">
                    {feedbackItems}
                </div>
            </div>
        </div>
    );
}

export default QuizResultPage;
