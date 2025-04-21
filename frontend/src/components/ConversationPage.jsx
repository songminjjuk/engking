import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const StartPage = () => {
    const location = useLocation();
    const { title, difficulty } = location.state || {};
    const navigate = useNavigate();

    const handleStartClick = () => {
        const userId = localStorage.getItem('userId'); // Retrieve userId from localStorage

        if (!userId) {
            alert('User ID is missing. Please log in.');
            return;
        }

        // Navigate to ConversationPage with title, difficulty, and userId
        navigate('/conversation', { state: { title, difficulty, memberId: userId } });
    };

    return (
        <div className="title-container">
            <h2 className="title-heading">대화를 시작하시겠읍니까 ?</h2>
            <h2 className="title-heading">선택한 난이도: {difficulty}</h2>
            <h2 className="title-heading">선택한 주제: {title}</h2>
            <button className="title-button" onClick={handleStartClick}> 시작하기 </button>
        </div>
    );
};

export default StartPage;
