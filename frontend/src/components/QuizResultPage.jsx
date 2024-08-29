import React from 'react';
import { useLocation } from 'react-router-dom';
import '../assets/css/result.css'

function QuizResultPage() {
    const location = useLocation();
    const { totalQuestions, correctAnswers } = location.state || { totalQuestions: 0, correctAnswers: 0 };

    return (
        <div className="result-container">
            <h2>Quiz Results</h2>
            <p>Total Questions Attempted: {totalQuestions}</p>
            <p>Correct Answers: {correctAnswers}</p>
            <p>Your Score: {totalQuestions > 0 ? ((correctAnswers / totalQuestions) * 100).toFixed(2) : 0}%</p>
        </div>
    );
}

export default QuizResultPage;
