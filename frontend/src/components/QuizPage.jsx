import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const QuizPage = () => {
    const location = useLocation();
    const { title, difficulty, userId } = location.state || {};
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [feedback, setFeedback] = useState("");
    const [answerSelected, setAnswerSelected] = useState(false);
    const [questions, setQuestions] = useState([]);
    const [chatRoomId, setChatRoomId] = useState('');
    const navigate = useNavigate();

    // Ref to track if questions have been fetched
    const questionsFetched = useRef(false);

    useEffect(() => {
        if (title && difficulty && userId && !questionsFetched.current) {
            fetchQuestions();
            questionsFetched.current = true; // Set flag to true after fetching
        }
    }, [title, difficulty, userId]);

    const parseQuestion = (questionText) => {
        if (!questionText) return { question: '', options: [] };

        const lines = questionText.split('\n').filter(line => line.trim() !== '');
        const question = lines[0]?.trim() || '';
        const options = lines.slice(1).map(line => {
            const option = line.split(') ')[1];
            return option ? option.trim() : '';
        }).filter(option => option !== '');
        return { question, options };
    };

    const fetchQuestions = async () => {
        try {
            const response = await axios.post('https://jback.engking.site/quiz/createquiz', {
                memberId: userId,
                quiz_type: title,
                difficulty: difficulty
            });

            const { success, chatRoomId, firstQuestion, messageId } = response.data;

            if (success) {
                setChatRoomId(chatRoomId);
                const { question, options } = parseQuestion(firstQuestion);
                if (question) {
                    setQuestions([{
                        question: question,
                        options: options,
                        messageId: messageId
                    }]);
                    setCurrentQuestionIndex(0); // Ensure index is reset correctly
                } else {
                    console.error('Parsed first question text is empty.');
                }
            } else {
                console.error('Failed to fetch questions.');
            }
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    };

    const handleAnswerClick = (option) => {
        if (answerSelected) return;

        setSelectedAnswer(option);
        setAnswerSelected(true);
        setFeedback("Answer selected. Click 'Next' to proceed.");
    };

    const fetchNextQuestion = async () => {
        try {
            const response = await axios.post('https://jback.engking.site/quiz/answer', {
                memberId: userId,
                chatRoomId: chatRoomId,
                messageId: questions[currentQuestionIndex].messageId,
                messageText: selectedAnswer,
                quiz_type: title,
                difficulty: difficulty
            });

            const { success, nextQuestion, messageId } = response.data;

            if (success) {
                const { question, options } = parseQuestion(nextQuestion);
                if (question) {
                    setQuestions(prevQuestions => [
                        ...prevQuestions,
                        {
                            question: question,
                            options: options,
                            messageId: messageId
                        }
                    ]);
                    setCurrentQuestionIndex(prevIndex => prevIndex + 1);
                    setSelectedAnswer(null);
                    setAnswerSelected(false);
                    setFeedback("");
                } else {
                    console.error('Parsed next question text is empty.');
                }
            } else {
                console.error('Failed to submit the answer.');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    };

    const handleNextClick = () => {
        if (!selectedAnswer) {
            setFeedback("Please select an answer.");
            return;
        }
        fetchNextQuestion();
    };

    const handleSaveClick = async () => {
        try {
            const response = await axios.post('https://jback.engking.site/quiz/endquiz', {
                chatRoomId: chatRoomId,
                memberId: userId,
                messageId: questions[currentQuestionIndex]?.messageId,
                endRequest: true
            });

            const { success, score, feedback: endFeedback } = response.data;

            if (success) {
                const totalQuestions = questions.length;
                const correctAnswers = Math.round(score * totalQuestions/100);

                navigate('/quizresult', {
                    state: {
                        totalQuestions: totalQuestions,
                        correctAnswers: correctAnswers, // Use calculated correct answers
                        score: score,
                        feedback: endFeedback
                    }
                });
            } else {
                console.error('Failed to end the quiz.');
            }
        } catch (error) {
            console.error('Error ending quiz:', error);
        }
    };

    if (!title || !difficulty || !chatRoomId || !userId || questions.length === 0) {
        return <div>Loading...</div>;
    }

    const currentQuestion = questions[currentQuestionIndex] || {};

    return (
        <div className="quiz-container">
            <h2>Question {currentQuestion.question || 'Loading question...'}</h2>
            <div className="options-container">
                {currentQuestion.options && currentQuestion.options.length > 0 ? (
                    currentQuestion.options.map((option, index) => (
                        <button
                            key={index}
                            className={`option-button ${selectedAnswer === option ? 'selected' : ''}`}
                            onClick={() => handleAnswerClick(option)}
                            disabled={answerSelected}
                        >
                            {option}
                        </button>
                    ))
                ) : (
                    <div>No options available</div>
                )}
            </div>
            {feedback && <div className="feedback">{feedback}</div>}
            <div className="actions-container">
                {answerSelected && (
                    <button onClick={handleNextClick} className="next-button">Next</button>
                )}
                <button onClick={handleSaveClick} className="save-button">Save</button>
            </div>
        </div>
    );
};

export default QuizPage;
