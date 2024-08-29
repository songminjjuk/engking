import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';


const StartPage = () => {
    const location = useLocation();
    const { title, difficulty } = location.state || {}; // Retrieve both title and difficulty from state
    const navigate = useNavigate();


    const handleStartClick = () => {
        // Navigate to Title page with selected difficulty as state
        navigate('/conversation', { state: { title, difficulty } });
    };

    return (
        <div className="title-container">
            <h2 className="title-heading">대화를 시작하시겠읍니까 ?</h2>
            <h2 className="title-heading">선택한 난이도: {difficulty}</h2> {/* Display the selected difficulty */}
            <h2 className="title-heading">선택한 주제: {title}</h2> {/* Display the selected title */}
            <button className="title-button" onClick={() => handleStartClick()}> 시작하기 </button>
        </div>
    );
};

export default StartPage;