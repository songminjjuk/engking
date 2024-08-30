import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Title = (props) => {
    const location = useLocation();
    const difficulty = location.state?.difficulty || 'Not selected'; // Get difficulty from state
    const [selectedTitle, setSelectedTitle] = useState(null);
    const navigate = useNavigate();

    const handleTitleClick = (title) => {
        setSelectedTitle(title);
        // Navigate to Title page with selected difficulty as state
        navigate('/start', { state: { title, difficulty } });
    };
    return (
        <div className="title-container">
            <h2 className="title-heading">주제를 선택하세요 ! 😆</h2>
            <h2 className="title-heading">선택한 난이도: {difficulty}</h2> {/* Display the selected difficulty */}
            <div className="button-grid">
                <button className="title-button" onClick={() => handleTitleClick('travel')}>여행</button>
                <button className="title-button" onClick={() => handleTitleClick('마트')}>마트</button>
                <button className="title-button" onClick={() => handleTitleClick('movie')}>영화</button>
                <button className="title-button" onClick={() => handleTitleClick('hamburger')}>음식</button>
                <button className="title-button" onClick={() => handleTitleClick('music')}>음악</button>
                <button className="title-button" onClick={() => handleTitleClick('meeting')}>회의</button>
                <button className="title-button" onClick={() => handleTitleClick('coffee')}>커피</button>
                <button className="title-button" onClick={() => handleTitleClick('교육')}>교육</button>
            </div>
        </div>
    );
};

export default Title;