import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import MicRecorder from 'mic-recorder-to-mp3';
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
    const [feedback, setFeedback] = useState('');
    const [feedbackResponse, setFeedbackResponse] = useState(null);
    const typingInterval = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const questionsFetched = useRef(false);
    const userId = localStorage.getItem('userId');
    const recorder = useRef(new MicRecorder({ bitRate: 128 }));

    const [questionAudioUrl, setQuestionAudioUrl] = useState('');
    const [userResponseAudioUrl, setUserResponseAudioUrl] = useState('');
    console.log(userId);
    useEffect(() => {
        if (title && difficulty && userId && !questionsFetched.current) {
            fetchFirstQuestion();
            questionsFetched.current = true;
        }
    }, [userId, title, difficulty]);

    const fetchFirstQuestion = async () => {
        try {
            if (!userId) {
                throw new Error('User ID is not available.');
            }

            const response = await axios.post('http://13.115.48.150:8080/chat/firstquestion', {
                memberId: userId,
                topic: title,
                difficulty: difficulty
            });

            const { success, firstQuestion, audioFileUrl, chatRoomId, messageId } = response.data;
            if (success) {
                setQuestions([{ text: '  ' + firstQuestion, audioFileUrl }]);
                setQuestionAudioUrl(audioFileUrl);
                setChatRoomId(chatRoomId);
                setMessageId(messageId);
                setTypingFinished(false);
                console.log(audioFileUrl);
            } else {
                console.error('Failed to fetch the first question.');
            }
        } catch (error) {
            setQuestions([{ text: 'First Question', audioUrl }]);
            setQuestionAudioUrl('');
            setChatRoomId('1');
            setMessageId('1');
            setTypingFinished(false);
        }
    };



    const uploadToS3 = async (mp3Blob) => {
        try {
            const fileName = `audio_${new Date().getTime()}.mp3`;

            // Get a presigned URL from the server
            const presignedResponse = await axios.post('http://13.115.48.150:8080/audio/uploadurl', {
                chatRoomId: chatRoomId,
                memberId: localStorage.getItem('userId'),
                messageId: String(Number(messageId) + 1)
            });

            const { audioFileUrl, success } = presignedResponse.data;
            if (!success) {
                throw new Error('Failed to get presigned URL from the server');
            }
            const preSignedUrl = audioFileUrl;

            // Upload the MP3 to S3 using the presigned URL
            const uploadResponse = await axios.put(preSignedUrl, mp3Blob, {
                headers: {
                    'Content-Type': 'audio/mp3',
                },
            });

            console.log('Upload Response Status:', uploadResponse.status);

            return preSignedUrl.split('?')[0];
        } catch (error) {
            console.error('Error uploading file to S3:', error);
            throw error;
        }
    };

    const handleNextQuestion = async () => {
        if (audioUrl) {
            try {
                // Upload audio file to S3
                const response = await fetch(audioUrl);
                const audioBlob = await response.blob();
                const mp3Blob = new Blob([audioBlob], { type: 'audio/mp3' }); // Use the same blob
                const s3Url = await uploadToS3(mp3Blob);

                if (!s3Url) {
                    throw new Error('Failed to upload audio to S3');
                }

                const responseNextQuestion = await axios.post('http://13.115.48.150:8080/chat/nextquestion', {
                    memberId: localStorage.getItem('userId'),
                    chatRoomId: chatRoomId,
                    messageId: String(Number(messageId) + 1),
                    topic: title,
                    difficulty: difficulty
                });

                const { success, nextQuestion, audioUrl: newAudioUrl, messageId: newMessageId } = responseNextQuestion.data;
                if (success) {
                    setQuestions(prevQuestions => [...prevQuestions, { text: nextQuestion, audioUrl: newAudioUrl }]);
                    setUserResponseAudioUrl(s3Url);
                    setMessageId(newMessageId);
                    setQuestionIndex(prevIndex => prevIndex + 1);
                    setCurrentText('');
                    setAudioUrl(null);
                    setIsRecording(false);
                    setTypingFinished(false);
                } else {
                    console.error('Failed to fetch the next question.');
                }
            } catch (error) {
                console.error('Error processing the next question:', error);
            }
        }
    };

    const submitFeedback = async () => {
        try {
            if (!userId || !chatRoomId || !messageId) {
                throw new Error('Required data is missing.');
            }
    
            const response = await axios.post('http://13.115.48.150:8080/chat/endquestion', {
                memberId: userId,
                chatRoomId: chatRoomId,
                messageId: messageId,
                endRequest: true
            });
    
            const { success, feedback: responseFeedback, score, endQuestion, audioFileUrl } = response.data;
            if (success) {
                setFeedbackResponse({ feedback: responseFeedback, score, endQuestion, audioFileUrl });
    
                // Navigate to convresult with feedback and additional data
                navigate('/convresult', {
                    state: {
                        title: title,
                        difficulty: difficulty,
                        feedback: responseFeedback,
                        score: score,
                        endQuestion: endQuestion,
                        audioFileUrl: audioFileUrl
                    }
                });
            } else {
                console.error('Failed to submit feedback.');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    };
    

    const handleMicClick = () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
        setIsRecording(prevState => !prevState);
    };

    const startRecording = () => {
        recorder.current.start().then(() => {
            console.log("Recording started");
        }).catch(error => {
            console.error('Error starting recording:', error);
        });
    };

    const stopRecording = async () => {
        try {
            const [buffer] = await recorder.current.stop().getMp3(); // Stop recording and get MP3 buffer
            const mp3Blob = new Blob(buffer, { type: 'audio/mp3' });
            setAudioUrl(URL.createObjectURL(mp3Blob));
        } catch (error) {
            console.error('Error stopping recording:', error);
        }
    };

    const handleDownload = () => {
        if (audioUrl) {
            const link = document.createElement('a');
            link.href = audioUrl;
            link.download = 'recording.mp3'; // Set the correct file extension
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    const handleSendClick = async () => {
        const feedbackData = await submitFeedback();
        if (feedbackData) {
            navigate('/convresult', { state: feedbackData });
        }
    };

    useEffect(() => {
        if (questions.length > 0 && !typingFinished) {
            typeQuestion(questions[questionIndex]?.text || '');
        }
        return () => {
            if (typingInterval.current) {
                clearInterval(typingInterval.current);
            }
        };
    }, [questionIndex, questions, typingFinished]);

    const typeQuestion = (question) => {
        let charIndex = 0;
        setCurrentText('');
        setTypingFinished(false);
        if (typingInterval.current) {
            clearInterval(typingInterval.current);
        }

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

    return (
        <div className="conv-page">
            <div className="conv-messages-container">
                {questions.length > 0 && questions.slice(0, questionIndex + 1).map((question, index) => (
                    <div key={index} className="conv-message conv-character-message">
                        <img
                            src={bbongssoon}
                            alt="Character"
                            className="conv-character-image"
                        />
                        <div className="conv-message-content">
                            <span>{`Q${index + 1}. ${index < questionIndex ? question.text : (index === questionIndex ? currentText : '')}`}</span>
                            {question.audioFileUrl && index === questionIndex && (
                                <div className="conv-audio-player">
                                    <audio controls src={question.audioFileUrl}></audio>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {questionIndex < questions.length && typingFinished && (
                    <div className="conv-message conv-user-message">
                        <img
                            src={usagi}
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
                                        <button
                                            className="conv-button"
                                            onClick={handleDownload}
                                        >
                                            Download
                                        </button>
                                        <audio controls src={audioUrl}></audio>
                                    </div>
                                )}
                                <button
                                    className="conv-button"
                                    onClick={handleNextQuestion}
                                    disabled={!audioUrl}
                                >
                                    Next
                                </button>
                                <button
                                    className="conv-button"
                                    onClick={handleSendClick}
                                >
                                    Send Feedback
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