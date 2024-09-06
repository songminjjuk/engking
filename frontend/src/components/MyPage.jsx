import React, { useState, useEffect, memo } from 'react';
import { Link } from 'react-router-dom';
import defaultProfileImage from '../assets/img/민석.jpg'; // Default profile image
import Modal from './Modal'; // Import the Modal component
import axios from 'axios'; // Import axios for HTTP requests

function MyPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [chatMessages, setChatMessages] = useState([]); // State for storing chat messages
  const [memberData, setMemberData] = useState(null); // State for storing member data
  const [conversationHistory, setConversationHistory] = useState([]); // State for storing conversation history

  // Get email and memberId from localStorage or any other source
  const email = localStorage.getItem('email'); // Example: Adjust this based on how you store the email
  const memberId = localStorage.getItem('userId'); // Assuming you store the user ID as 'userId'
  console.log(email);
  // Function to fetch member data
  const fetchMemberData = async () => {
    try {
      if (email) {
        const response = await axios.post(`http://35.72.9.14:8080/member/info?email=${email}`);
  
        console.log('API Response:', response.data);
        setMemberData(response.data);
      } else {
        console.error('Email is missing.');
      }
    } catch (error) {
      console.error('Error fetching member data:', error);
    }
  };
  // Function to fetch conversation history
  const fetchConversationHistory = async () => {
    try {
      if (memberId) {
        const response = await axios.post('http://13.115.48.150:8080/chatroom/chatroomlist', {
          memberId: memberId
          
        });
        console.log(memberId);
        console.log('Conversation History Response:', response.data);
        setConversationHistory(response.data);
      } else {
        console.error('Member ID is missing.');
      }
    } catch (error) {
      console.error('Error fetching conversation history:', error);
    }
  };

  // Function to fetch chat messages
  const fetchChatMessages = async (chatRoomId) => {
    try {
      if (memberId) {
        const response = await axios.post('http://13.115.48.150:8080/chatmessage/allmessages', {
          memberId: memberId,
          chatRoomId: chatRoomId
        });

        console.log('Chat Messages Response:', response.data);
        setChatMessages(response.data);
      } else {
        console.error('Member ID is missing.');
      }
    } catch (error) {
      console.error('Error fetching chat messages:', error);
    }
  };

  // Function to delete a chat room
  const handleDeleteChatRoom = async (chatRoomId) => {
    const confirmed = window.confirm('Are you sure you want to delete this chat room?');
    if (!confirmed) return;

    try {
      if (memberId) {
        const response = await axios.post('http://13.115.48.150:8080/chatroom/deletechatroom', {
          memberId: memberId, 
          chatRoomId: chatRoomId
        });

        if (response.data.queryResult) {
          setConversationHistory(prevHistory => prevHistory.filter(room => room.chatRoomId !== chatRoomId));
        } else {
          console.error('Failed to delete the chat room.');
        }
      } else {
        console.error('Member ID is missing.');
      }
    } catch (error) {
      console.error('Error deleting chat room:', error);
    }
  };

  useEffect(() => {
    fetchMemberData();
    fetchConversationHistory();
  }, []);

  const handleCardClick = (history) => {
    setSelectedHistory(history);
    fetchChatMessages(history.chatRoomId);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedHistory(null);
    setChatMessages([]);
  };

  const conversationList = conversationHistory.filter(room => (room.topic || '').trim() !== '');
  const quizList = conversationHistory.filter(room => !room.topic || (room.topic || '').trim() === '');

  return (
    <div className="my-page-container">
      {/* Profile Section */}
      <div className="profile-section">
        <button className="mypage-button">{memberData?.name || 'mypage'}</button>
        <div className="profile-info">
          <img
            src={memberData?.profileImgUrl || defaultProfileImage} // Check if profileImgUrl exists
            alt="User Profile"
            onError={(e) => {
              e.target.onerror = null; // Prevent infinite loop if default image fails
              e.target.src = defaultProfileImage; // Fallback to default image on error
            }}
            className="profile-image"
          />
          <div className="profile-details">
            {memberData ? (
              <>
                <div>
                  <strong>이름:</strong> <span>{memberData.name}</span>
                </div>
                <div>
                  <strong>전화번호:</strong> <span>{memberData.phone || 'N/A'}</span>
                </div>
                <div>
                  <strong>생일:</strong> <span>{memberData.birthday || 'N/A'}</span>
                </div>
                <div>
                  <strong>이메일:</strong> <span>{memberData.email}</span>
                </div>
              </>
            ) : (
              <p>Loading profile...</p>
            )}
            <Link to="/edit-info">
              <button className="edit-info-button">
                정보 수정
              </button>
            </Link>
          </div>
        </div>
      </div>

      {/* History Section */}
      <div className="history-section">
        {/* Conversation History */}
        {conversationList.length > 0 && (
          <>
            <h2>Conversation History</h2>
            <div className="history-cards">
              {conversationList.map((chatRoom, index) => (
                <div key={index} className="history-card">
                  <div onClick={() => handleCardClick(chatRoom)}>
                    <span>{new Date(chatRoom.createdTime).toLocaleDateString()}</span>
                    <p>Topic: {chatRoom.topic}</p>
                    <p>Difficulty: {chatRoom.difficulty}</p>
                    <p>Score: {chatRoom.queryResult ? 'Completed' : 'Incomplete'}</p>
                  </div>
                  <button className="delete-button" onClick={() => handleDeleteChatRoom(chatRoom.chatRoomId)}>Delete</button>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Quiz History */}
        {quizList.length > 0 && (
          <>
            <h2>Quiz History</h2>
            <div className="history-cards">
              {quizList.map((chatRoom, index) => (
                <div key={index} className="history-card">
                  <div onClick={() => handleCardClick(chatRoom)}>
                    <span>{new Date(chatRoom.createdTime).toLocaleDateString()}</span>
                    <p>Difficulty: {chatRoom.difficulty}</p>
                    <p>Score: {chatRoom.queryResult ? 'Completed' : 'Incomplete'}</p>
                  </div>
                  <button className="delete-button" onClick={() => handleDeleteChatRoom(chatRoom.chatRoomId)}>Delete</button>
                </div>
              ))}
            </div>
          </>
        )}

        {/* If no data available */}
        {conversationList.length === 0 && quizList.length === 0 && (
          <p>No history found.</p>
        )}
      </div>

      {/* Modal for detailed history view */}
      <Modal show={showModal} onClose={handleCloseModal}>
        {selectedHistory && (
          <>
            <h3 style={{ fontWeight: 700 }}>{new Date(selectedHistory.createdTime).toLocaleDateString()}</h3>
            <p><strong>📆 Date:</strong> {new Date(selectedHistory.createdTime).toLocaleDateString()}</p>
            <p><strong>📝 Topic:</strong> {selectedHistory.topic}</p>
            <p><strong>🎯 Difficulty:</strong> {selectedHistory.difficulty}</p>
            <p><strong>✅ Status:</strong> {selectedHistory.queryResult ? 'Completed' : 'Incomplete'}</p>

            <h4>💬 Chat Messages:</h4>
            {chatMessages.length > 0 ? (
              chatMessages.map((message, index) => (
                <div key={index} className="message-item">
                  <p><strong>{message.senderId}:</strong> {message.messageText}</p>
                  <p><em>{new Date(message.messageTime).toLocaleTimeString()}</em></p>
                  {message.AudioFileUrl && (
                    <p>
                      <audio controls>
                        <source src={message.AudioFileUrl} type="audio/mp3" />
                        Your browser does not support the audio element.
                      </audio>
                    </p>
                  )}
                  {message.feedback && (
                    <p><strong>Feedback</strong> {message.feedback}</p>
                  )}
                </div>
              ))
            ) : (
              <p>No messages found.</p>
            )}
          </>
        )}
      </Modal>
    </div>
  );
}

export default MyPage;
