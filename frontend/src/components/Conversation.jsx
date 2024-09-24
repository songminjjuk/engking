import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import MicRecorder from 'mic-recorder-to-mp3';
import bbongssoon from '../assets/img/bbongssoon.jpg';
import usagi from '../assets/img/농담곰.jpeg';
import '../assets/css/conv.css';
import Loading from './Loading';

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
    const [loading, setLoading] = useState(false); // Add loading state
    const typingInterval = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const questionsFetched = useRef(false);
    const userId = localStorage.getItem('userId');
    const recorder = useRef(new MicRecorder({ bitRate: 128 }));
    const [fileName, setFileName] = useState('');
    const [questionAudioUrl, setQuestionAudioUrl] = useState('');
    const [userResponseAudioUrl, setUserResponseAudioUrl] = useState('');

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

            const response = await axios.post('https://nback.engking.site/api/first-question/', {
                memberId: userId,
                topic: title,
                difficulty: difficulty
            });

            const { success, firstQuestion, audioUrl, chatRoomId, messageId } = response.data;
            if (success) {
                setQuestions([{ text: '  ' + firstQuestion, audioUrl }]);
                setQuestionAudioUrl(audioUrl);
                setChatRoomId(chatRoomId);
                setMessageId(messageId);
                setTypingFinished(false);
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
            const fileName = `${userId}/${chatRoomId}/${Number(messageId) + 1}.mp3`;
            setFileName(fileName);
            console.log("File Name:", fileName);
            console.log("Blob size:", mp3Blob.size);
    
            // Get a presigned URL from the server
            const presignedResponse = await axios.post('https://nback.engking.site/api/create-put-url/', {
                filename: 'test',
                // header: {
                //     "Content-Length": String(mp3Blob.size),  // Provide the correct content length
                // },
            });
    
            const { presignedUrl, success } = presignedResponse.data;
            if (!success) {
                throw new Error('Failed to get presigned URL from the server');
            }
    
            console.log("Presigned URL:", presignedUrl);
    
            // Convert the mp3Blob into a File object
            const audioFile = new File([mp3Blob], fileName, { type: 'audio/mp3' });
            console.log("Audio File Type:", audioFile.type);
    
            // Upload the MP3 to S3 using the presigned URL
            const uploadResponse = await fetch(presignedUrl, {
                method: 'PUT',
                // headers: {  // Fix header to headers
                //     "Content-Type": 'audio/mp3',  // Ensure proper Content-Type
                //     "Content-Length": String(mp3Blob.size),  // Add correct size
                // },
                body: 'test',  // Pass the File object as the body
            });
            console.log(uploadResponse.httpResponse);
    
            console.log('Upload Response Status:', uploadResponse.status);
    
            if (!uploadResponse.ok) {
                throw new Error(`Upload failed with status ${uploadResponse.status}`);
            }
    
            // Return the file URL (without query parameters)
            return presignedUrl.split('?')[0];
        } catch (error) {
            console.error('Error uploading file to S3:', error);
            console.log(this.request.httpResponse);
            console.log(this.httpResponse);
            throw error;
        }
    };
    
    const handleNextQuestion = async () => {
        if (audioUrl) {
            setLoading(true); // Set loading state to true before making the request
            try {
                // Upload audio file to S3
                const response = await fetch(audioUrl);
                const audioBlob = await response.blob();
                const mp3Blob = new Blob([audioBlob], { type: 'audio/mp3' }); // Use the same blob
                const s3Url = await uploadToS3(mp3Blob);

                if (!s3Url) {
                    throw new Error('Failed to upload audio to S3');
                }
                console.log(s3Url);
                const tmp = `${userId}/${chatRoomId}/${Number(messageId) + 1}.mp3`;
                console.log("response",audioUrl);
                console.log(tmp);
                const responseNextQuestion = await axios.post('https://nback.engking.site/api/next-question/', {
                    memberId: String(localStorage.getItem('userId')),
                    chatRoomId: String(chatRoomId), // Use existing chatRoomId from state
                    messageId: String(Number(messageId) + 1),
                    filename: tmp,
                    topic: title,
                    difficulty: difficulty
                });
    
                const { success, nextQuestion, audioUrl: newAudioUrl, chatRoomId: newChatRoomId, messageId: newMessageId } = responseNextQuestion.data;
    
                if (success) {
                    setQuestions(prevQuestions => [...prevQuestions, { text: '  ' + nextQuestion, audioUrl: newAudioUrl }]);
                    setUserResponseAudioUrl(s3Url);
                    setChatRoomId(newChatRoomId); // Update with the new chatRoomId
                    setMessageId(newMessageId); // Update with the new messageId
                    setAudioUrl(newAudioUrl);
                    setQuestionIndex(prevIndex => prevIndex + 1);
                    setCurrentText('');
                    setIsRecording(false);
                    setTypingFinished(false);
                } else {
                    console.error('Failed to fetch the next question.');
                }
            } catch (error) {
                console.error('Error processing the next question:', error);
            } finally {
                setLoading(false); // Set loading state to false after request completes
            }
        }
    };

    const submitFeedback = async () => {
        try {
            if (!userId || !chatRoomId || !messageId) {
                throw new Error('Required data is missing.');
            }
    
            const response = await axios.post('https://nback.engking.site/api/feedback/', {
                memberId: userId,
                chatRoomId: chatRoomId,
                messageId: messageId,
                responseText: ""
            });
    
            const { messageId, success, feedback, score, audioUrl } = response.data;
            if (success) {
                setFeedbackResponse({ feedback: feedback, score, audioUrl });
    
                // Navigate to convresult with feedback and additional data
                navigate('/convresult', {
                    state: {
                        title: title,
                        difficulty: difficulty,
                        feedback: feedback,
                        score: score,
                        // endQuestion: endQuestion,
                        audioFileUrl: audioUrl
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
                            {questionAudioUrl && index === questionIndex && (
                                <div className="conv-audio-player">
                                    <audio controls src={questionAudioUrl}></audio>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {!loading && <Loading loading={loading} />}
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
                                    disabled={!audioUrl || loading} // Disable button when loading
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
