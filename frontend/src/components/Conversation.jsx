import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import bbongssoon from '../assets/img/bbongssoon.jpg';
import usagi from '../assets/img/농담곰.jpeg';
import '../assets/css/conv.css';

const ConversationPage = () => {
    const location = useLocation();
    const { title, difficulty } = location.state || {};
    const navigate = useNavigate();

    const [isRecording, setIsRecording] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [questionIndex, setQuestionIndex] = useState(0);
    const [currentText, setCurrentText] = useState('');
    const [typingFinished, setTypingFinished] = useState(false);
    const [questions, setQuestions] = useState([]);
    const [chatRoomId, setChatRoomId] = useState('');
    const [messageId, setMessageId] = useState('');
    const typingInterval = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    useEffect(() => {
        const fetchFirstQuestion = async () => {
            try {
                const memberId = localStorage.getItem('userId'); // Retrieve member ID from localStorage
                if (!memberId) {
                    throw new Error('User ID is not available.');
                }

                const response = await axios.post('http://www.rapapa.site:8080/chat/firstquestion', {
                    memberId: memberId,
                    topic: title,
                    difficulty: difficulty
                });

                const { chatRoomId, messageId, firstQeustion } = response.data;
                setChatRoomId(chatRoomId);
                setMessageId(messageId);
                setQuestions([firstQeustion]);
            } catch (error) {
                console.error('Error fetching the first question:', error);
            }
        };

        fetchFirstQuestion();
    }, [title, difficulty]);

    useEffect(() => {
        if (questionIndex < questions.length) {
            setTypingFinished(false);
            typeQuestion(questions[questionIndex]);
        }
        return () => clearInterval(typingInterval.current);
    }, [questionIndex, questions]);

    const typeQuestion = (question) => {
        let charIndex = 0;
        setCurrentText('');
        typingInterval.current = setInterval(() => {
            setCurrentText(prev => {
                const newText = prev + question[charIndex];
                if (charIndex === question.length - 1) {
                    clearInterval(typingInterval.current);
                    setTypingFinished(true);
                }
                return newText;
            });
            charIndex++;
        }, 50);
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

    const handleSendClick = async () => {
        if (audioUrl) {
            try {
                const response = await axios.post('http://www.rapapa.site:8080/chat/nextquestion', {
                    memberId: localStorage.getItem('userId'), // Retrieve member ID from localStorage
                    chatRoomId: chatRoomId,
                    messageId: messageId,
                    messageText: 'Audio response placeholder', // Replace with the actual transcribed text or some placeholder
                });

                const { messageId: newMessageId, nextQeustion } = response.data;
                setMessageId(newMessageId);
                setQuestions(prevQuestions => [...prevQuestions, nextQeustion]);
                handleNextQuestion();
            } catch (error) {
                console.error('Error sending the audio response:', error);
            }
        }
    };

    const handleNextQuestion = () => {
        if (questionIndex < questions.length - 1) {
            setQuestionIndex(prevIndex => prevIndex + 1);
            setCurrentText('');
            setAudioUrl(null);
            setIsRecording(false);
            setTypingFinished(false);
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
                {questionIndex < questions.length && typingFinished && (
                    <div className="conv-message conv-user-message">
                        <img
                            src={usagi}  // User image
                            alt="User"
                            className="conv-user-image"
                        />
                        <div className="conv-user-message-content">
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
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConversationPage;
