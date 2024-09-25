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

    return (
        <div className="result-container">
            <div className="res_title">퀴즈 결과</div>
            <p><strong>전체 문제 수:</strong>{totalQuestions}</p>
            <p><strong>정답 문제 수:</strong> {correctAnswers}</p>
            <p><strong>점수:</strong> {score}%</p>
            <p><strong>결과 분석:</strong> {feedback}</p>
        </div>
    );
}

export default QuizResultPage;
