import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const QuizTitle = () => {
    const location = useLocation();
    const difficulty = location.state?.difficulty || 'Not selected'; // Get difficulty from state
    const [selectedTitle, setSelectedTitle] = useState(null);
    const navigate = useNavigate();

    const handleTitleClick = (title) => {
        setSelectedTitle(title);

        // Retrieve userId from localStorage
        const userId = localStorage.getItem('userId');

        if (!userId) {
            console.error('User ID not found in localStorage');
            return;
        }

        // Navigate to quiz page with title, difficulty, and userId
        navigate('/quiz', {
            state: {
                title,
                difficulty,
                userId
            }
        });
    };

    return (
        <div className="title-container">
            <h2 className="title-heading">주제를 선택하세요 ! 😆</h2>
            <h2 className="title-heading">선택한 난이도: {difficulty}</h2> {/* Display the selected difficulty */}
            <div className="quizbutton-grid">
                <button className="title-button" onClick={() => handleTitleClick('vocabulary')}>단어 퀴즈</button>
                <button className="title-button" onClick={() => handleTitleClick('grammar')}>문법 퀴즈</button>
            </div>
        </div>
    );
};

export default QuizTitle;
