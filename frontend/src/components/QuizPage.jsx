import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Loading from './Loading';

const QuizPage = () => {
    const location = useLocation();
    const { title, difficulty, userId } = location.state || {};
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [feedback, setFeedback] = useState("");
    const [questions, setQuestions] = useState([]); // Store all questions here
    const [chatRoomId, setChatRoomId] = useState('');
    const [loading, setLoading] = useState(false); // State to track loading status
    const navigate = useNavigate();
    const questionsFetched = useRef(false);
    const currentQuestion = questions.length > 0 ? questions[currentQuestionIndex] : {};

    // Fetch questions on initial load
    useEffect(() => {
        if (title && difficulty && userId && !questionsFetched.current) {
            fetchQuestions();
            questionsFetched.current = true;
        }
    }, [title, difficulty, userId]);

    // Back button handling
    const preventGoBack = () => {
        window.history.pushState(null, "", location.href);
    };

    useEffect(()=> {
        window.history.pushState(null, '', ''); // 현재 페이지 history stack 한개 더 쌓기
        window.onpopstate = () => {
            // Show a confirmation dialog instead of alert
            const userConfirmed = window.confirm('뒤로가기 실행 시 퀴즈 저장이 불가합니다 ! 그래도 뒤로 가시겠습니까? ');
    
            if (userConfirmed) {
                // If user clicks "Yes", navigate to the quiz start page
                navigate('/quiztitle',  { state: { difficulty } });
            } else {
                // If user clicks "No", push the current state again to prevent back navigation
                window.history.pushState(null, '', window.location.href);
            }
        };
    
        return () => {
            // Clean up the event listener on component unmount
            window.onpopstate = null;
        };
    
    },[navigate]);
    
    const parseQuestion = (questionText) => {
        if (!questionText) return { question: '', options: [] };
        const cleanedText = questionText.replace(/^[^0-9]*[0-9]+\.\s*/, '');
        const lines = cleanedText.split('\n').filter(line => line.trim() !== '');
        let question = lines[0]?.trim() || '';
        const middleSentence = lines.length - 4 > 1 ? lines[1]?.trim() : '';
        if (middleSentence) {
            question += '\n' + middleSentence;
        }
        const optionsStartIndex = middleSentence ? 2 : 1;
        const options = lines.slice(optionsStartIndex).map(line => {
            const match = line.match(/^[A-D]\)\s*(.*)$/);
            return match ? match[1].trim() : '';
        }).filter(option => option !== '');
        return { question, options };
    };

    const fetchQuestions = async () => {
        try {
            setLoading(true);
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
                    setQuestions([{ question: question, options: options, messageId: messageId }]);
                    setCurrentQuestionIndex(0); // Start at the first question
                } else {
                    console.error('Parsed first question text is empty.');
                }
            } else {
                console.error('Failed to fetch questions.');
            }
        } catch (error) {
            console.error('Error fetching questions:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchNextQuestion = async () => {
        try {
            setLoading(true);
            const response = await axios.post('https://jback.engking.site/quiz/answer', {
                memberId: userId,
                chatRoomId: chatRoomId,
                messageId: String(Number(questions[currentQuestionIndex].messageId) + 1),
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
                        { question: question, options: options, messageId: messageId }
                    ]);
                    setCurrentQuestionIndex(prevIndex => prevIndex + 1);
                    setSelectedAnswer(null);
                    setFeedback("");
                } else {
                    console.error('Parsed next question text is empty.');
                }
            } else {
                console.error('Failed to submit the answer.');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerClick = (option) => {
        setSelectedAnswer(option);
        setFeedback("Answer selected. Click 'Next' to proceed.");
    };

    const handleNextClick = () => {
        if (!selectedAnswer) {
            setFeedback("Please select an answer.");
            return;
        }
        fetchNextQuestion();
    };

    const handlePreviousClick = async () => {
        if (currentQuestionIndex > 0) {
            try {
                setLoading(true); 
                // Make the DELETE request to the /deletemessage endpoint
                const response = await axios.post('https://jback.engking.site/chatmessage/deletemessage', {
                    memberId: String(userId),     // Properly passing memberId
                    chatRoomId: String(chatRoomId), // Properly passing chatRoomId
                    messageId: String(questions[currentQuestionIndex]?.messageId)  // Properly passing messageId
                }, {
                    headers: {
                        'Content-Type': 'application/json'  // Ensuring correct Content-Type header
                    }
                });
    
                // Check for the 204 No Content status
                if (response.status === 204) {
                    // Successfully deleted the message, now update the state to show the previous question
                    setCurrentQuestionIndex(prevIndex => prevIndex - 1);
                    setSelectedAnswer(null);
                    setFeedback("");  // Clear any previous feedback
                } else {
                    setFeedback('Failed to delete the message.');
                    console.error('Failed to delete the message. Status:', response.status);
                }
            } catch (error) {
                setFeedback('Error communicating with the server.');
                console.error('Error deleting the message:', error);
            } finally {
                setLoading(false);  // Remove the loading spinner
            }
        } else {
            setFeedback("This is the first question.");
        }
    };
    
    

    const handleSaveClick = async () => {
        try {
            setLoading(true);
            const response = await axios.post('https://jback.engking.site/quiz/endquiz', {
                chatRoomId: chatRoomId,
                memberId: userId,
                messageId: questions[currentQuestionIndex]?.messageId,
                messageText: selectedAnswer,
                quiz_type: title,
                difficulty: difficulty,
                endRequest: true
            });
            const { success, score, feedback: endFeedback } = response.data;
            if (success) {
                const totalQuestions = currentQuestionIndex+1;
                const correctAnswers = Math.round(parseFloat(score) * parseInt(totalQuestions) / 100);
                navigate('/quizresult', {
                    state: {
                        totalQuestions: totalQuestions,
                        correctAnswers: correctAnswers,
                        score: score,
                        feedback: endFeedback
                    }
                });
            } else {
                console.error('Failed to end the quiz.');
            }
        } catch (error) {
            console.error('Error ending quiz:', error);
        } finally {
            setLoading(false);
        }
    };

    // Show loading indicator while data is being fetched
    if (!title || !difficulty || !chatRoomId || !userId || questions.length === 0) {
        return <Loading loading={loading} />;
    }

    return (
        <div className="quiz-container">
            <h2>Question {currentQuestionIndex + 1}. {currentQuestion.question || <Loading loading={loading} />}</h2>
            <div className="options-container">
                {currentQuestion.options && currentQuestion.options.length > 0 ? (
                    currentQuestion.options.map((option, index) => (
                        <button
                            key={index}
                            className={`option-button ${selectedAnswer === option ? 'selected' : ''}`}
                            onClick={() => handleAnswerClick(option)}
                        >
                            {option}
                        </button>
                    ))
                ) : (
                    <div>No options available</div>
                )}
            </div>
            {loading && <Loading loading={loading} />}
            {feedback && <div className="feedback">{feedback}</div>}
            <div className="actions-container">
                {currentQuestionIndex > 0 && (
                    <button onClick={handlePreviousClick} className="next-button">Previous</button>
                )}
                {selectedAnswer && (
                    <button onClick={handleNextClick} className="next-button">Next</button>
                )}
                <button onClick={handleSaveClick} className="save-button">Save and Quit</button>
            </div>
        </div>
    );
};

export default QuizPage;
