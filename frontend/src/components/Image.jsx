import React from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate from react-router-dom

const Image = (props) => {
    const navigate = useNavigate(); // Initialize the useNavigate hook

    const handleAboutClick = () => {
        if (props.isLoggedIn) {
            navigate('/about'); // Navigate to the about page if logged in
        } else {
            alert("로그인 후 이용 가능합니다 !"); // Show an alert
            navigate('/login'); // Redirect to the login page if not logged in
        }
    };

    const handleQuizClick = () => {
        if (props.isLoggedIn) {
            navigate('/quizdiffi'); // Navigate to the quiz difficulty page if logged in
        } else {
            alert("로그인 후 이용 가능합니다 !"); // Show an alert
            navigate('/login'); // Redirect to the login page if not logged in
        }
    };

    return (
        <section id="imageType" className={`imageType__wrap ${props.element}`}>
            <h2>{props.title}</h2>
            <p>AI 기반 영어 회화 연습 서비스</p>
            <div className="image__inner container">
                <article className="image img1">
                    <h3 className="image__title">영어 회화 연습</h3>
                    <p className="image__desc">AI와 함께 회화 연습을 !</p>
                    <button className="image__btn" onClick={handleAboutClick}>
                        하러 가기
                    </button>
                </article>
                <article className="image img2">
                    <h3 className="image__title">단어 / 문법 퀴즈</h3>
                    <p className="image__desc">AI와 함께 퀴즈를 !</p>
                    <button className="image__btn yellow" onClick={handleQuizClick}>
                        하러 가기
                    </button>
                </article>
            </div>
        </section>
    );
};

export default Image;
