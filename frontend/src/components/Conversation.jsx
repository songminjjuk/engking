import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import bbongssoon from '../assets/img/bbongssoon.jpg';
import micImage from '../assets/img/mic.png';
import pauseImage from '../assets/img/pause.png';
import '../assets/css/conv.css';

const ConversationPage = () => {
    const location = useLocation();
    const { title, difficulty } = location.state || {};
    const navigate = useNavigate();

    const [isRecording, setIsRecording] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [questionIndex, setQuestionIndex] = useState(0);
    const [currentText, setCurrentText] = useState('');
    const typingInterval = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const questions = [
        "  What’s something simple that brings you joy?",
        "  If you could travel anywhere in the world, where would you go?",
        "  What’s your favorite way to relax after a long day?",
        "  Can you tell me about a recent challenge you faced and how you overcame it?",
        "  What’s a skill you’d like to learn and why?"
    ];

    useEffect(() => {
        if (questionIndex < questions.length) {
            typeQuestion(questions[questionIndex]);
        }
        return () => clearInterval(typingInterval.current); // Clean up the interval on unmount
    }, [questionIndex]);

    const typeQuestion = (question) => {
        let charIndex = 0;
        setCurrentText(''); // Reset current text
        typingInterval.current = setInterval(() => {
            setCurrentText(prev => {
                const newText = prev + question[charIndex];
                if (charIndex === question.length - 1) {
                    clearInterval(typingInterval.current);
                }
                return newText;
            });
            charIndex++;
        }, 50); // Adjust typing speed here
    };

    const handleMicClick = () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
        setIsRecording(prevState => !prevState);
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            mediaRecorderRef.current.ondataavailable = event => {
                audioChunksRef.current.push(event.data);
            };
            mediaRecorderRef.current.start();
        } catch (err) {
            console.error("Error accessing microphone", err);
        }
    };

    const stopRecording = () => {
        mediaRecorderRef.current.stop();
        mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(audioBlob);
            setAudioUrl(audioUrl);
            audioChunksRef.current = [];
        };
    };

    const handleSendClick = () => {
        navigate('/convresult', {
            state: {
                audioUrl,
                title,
                difficulty
            }
        });
    };

    const handleNextQuestion = () => {
        if (questionIndex < questions.length - 1) {
            setQuestionIndex(prevIndex => prevIndex + 1);
            setCurrentText(''); // Clear current text for the next question
            setAudioUrl(null);
            setIsRecording(false);
        }
    };

    return (
        <div className="conv-page">
            <div className="conv-messages-container">
                {questions.slice(0, questionIndex + 1).map((question, index) => (
                    <div key={index} className="conv-message conv-character-message">
                        <img
                            src={bbongssoon}
                            alt="Character"
                            className="conv-character-image"
                        />
                        <div className="conv-message-content">
                            <span>{`Q${index + 1}. ${index < questionIndex ? question : (index === questionIndex ? currentText : '')}`}</span>
                        </div>
                    </div>
                ))}
                {questionIndex < questions.length && (
                    <div className="conv-buttons-bubble">
                        <div className="conv-button-container">
                            <button
                                className="conv-button"
                                onClick={handleMicClick}
                            >
                                {isRecording ? 'Pause' : 'Start Recording'}
                            </button>
                            {audioUrl && (
                                <div className="conv-audio-player">
                                    <h3>Your Recording:</h3>
                                    <audio controls src={audioUrl}></audio>
                                </div>
                            )}
                            <button className="conv-button" onClick={handleSendClick}>
                                Send
                            </button>
                            <button className="conv-button" onClick={handleNextQuestion}>
                                Next Question
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConversationPage;
