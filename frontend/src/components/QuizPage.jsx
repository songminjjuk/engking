import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function QuizPage() {
    const questions = [
        {
            question: "Q1. Which of the following is a synonym of 'happy'?",
            options: ["Sad", "Angry", "Joyful", "Tired"],
            correctAnswer: "Joyful"
        },
        {
            question: "Q2. What is the opposite of 'difficult'?",
            options: ["Easy", "Hard", "Complex", "Challenging"],
            correctAnswer: "Easy"
        },
        // Add more questions here
    ];

    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [feedback, setFeedback] = useState("");
    const [answerSelected, setAnswerSelected] = useState(false);
    const [correctAnswers, setCorrectAnswers] = useState(0); // Track correct answers

    const navigate = useNavigate(); // Initialize useNavigate for navigation

    const { question, options, correctAnswer } = questions[currentQuestionIndex];

    const handleAnswerClick = (option) => {
        if (answerSelected) return;

        setSelectedAnswer(option);
        if (option === correctAnswer) {
            setFeedback("Correct! 🎉");
            setCorrectAnswers(correctAnswers + 1); // Increment correct answers
        } else {
            setFeedback("Oops! That's incorrect 😂");
        }
        setAnswerSelected(true);
    };

    const handleNextClick = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setSelectedAnswer(null);
            setFeedback("");
            setAnswerSelected(false);
        }
    };

    const handleSaveClick = () => {
        // Navigate to the result page and pass the data
        navigate('/quizresult', {
            state: {
                totalQuestions: currentQuestionIndex + 1, // Only count the questions attempted so far
                correctAnswers: correctAnswers
            }
        });
    };

    return (
        <div className="quiz-container">
            <h2>{question}</h2>
            <div className="options-container">
                {options.map((option, index) => (
                    <button
                        key={index}
                        className={`option-button ${selectedAnswer === option ? 'selected' : ''}`}
                        onClick={() => handleAnswerClick(option)}
                        disabled={answerSelected}
                    >
                        {option}
                    </button>
                ))}
            </div>
            {feedback && <div className="feedback">{feedback}</div>}
            {answerSelected && (
                <div className="actions-container">
                    {currentQuestionIndex < questions.length - 1 && (
                        <button onClick={handleNextClick} className="next-button">Next</button>
                    )}
                    <button onClick={handleSaveClick} className="save-button">Save</button>
                </div>
            )}
        </div>
    );
}

export default QuizPage;
