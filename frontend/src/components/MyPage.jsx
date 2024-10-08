import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import defaultProfileImage from '../assets/img/bbongssoon.jpg';
import Modal from './Modal';
import axios from 'axios';
import Calendar from 'react-calendar';
import moment from 'moment/moment';


function MyPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [memberData, setMemberData] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [dateClicked, setDateClicked] = useState(new Date());
  const [events, setEvents] = useState([]);

  const email = localStorage.getItem('email');
  const memberId = localStorage.getItem('userId');

  const fetchMemberData = async () => {
    try {
      if (email) {
        const response = await axios.post(`https://sback.engking.site/member/info?email=${email}`);
        setMemberData(response.data);
      } else {
        console.error('Email is missing.');
      }
    } catch (error) {
      console.error('Error fetching member data:', error);
    }
  };

  const fetchConversationHistory = async () => {
    try {
      if (memberId) {
        const response = await axios.post('https://jback.engking.site/chatroom/chatroomlist', {
          memberId: memberId,
        });
        setConversationHistory(response.data);

        const eventsData = response.data.map(room => ({
          date: new Date(room.createdTime),
          topic: room.topic,
          difficulty: room.difficulty,
        }));
        setEvents(eventsData);
        console.log('event day: ', eventsData);
      } else {
        console.error('Member ID is missing.');
      }
    } catch (error) {
      console.error('Error fetching conversation history:', error);
    }
  };

  const fetchChatMessages = async (chatRoomId) => {
    try {
      if (memberId) {
        const response = await axios.post('https://jback.engking.site/chatmessage/allmessages', {
          memberId: memberId,
          chatRoomId: chatRoomId,
        });
        setChatMessages(response.data);
      } else {
        console.error('Member ID is missing.');
      }
    } catch (error) {
      console.error('Error fetching chat messages:', error);
    }
  };

  const handleDeleteChatRoom = async (chatRoomId) => {
    const confirmed = window.confirm('정말 삭제하시겠습니까?');
    if (!confirmed) return;
    try {
      if (memberId) {
        const response = await axios.post('https://jback.engking.site/chatroom/deletechatroom', {
          memberId: memberId,
          chatRoomId: chatRoomId,
        });
        if (response.data.queryResult) {
          setConversationHistory(prevHistory => prevHistory.filter(room => room.chatRoomId !== chatRoomId));
          alert('삭제되었습니다!');
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

  const handleDateChange = (date) => {
    setDateClicked(date);
  };

  const renderEvents = () => {
    const eventsOnSelectedDate = events.filter(event => event.date.toDateString() === dateClicked.toDateString());
    return eventsOnSelectedDate.length > 0 ? (
      <ul>
        {eventsOnSelectedDate.map((event, index) => (
          <li key={index}>
            <strong>Topic:</strong> {event.topic} <br />
            <strong>Difficulty:</strong> {event.difficulty}
          </li>
        ))}
      </ul>
    ) : (
      <p>No events found on this date.</p>
    );
  };

  const conversationList = conversationHistory.filter(room => (room.topic || '').trim() !== '');
  const quizList = conversationHistory.filter(room => !room.topic || (room.topic || '').trim() === '');

  return (
    <div className="my-page-container">
      <div className="profile-container">
        <div className="profile-section">
          <button className="mypage-button">{memberData?.name || 'mypage'}</button>
          <div className="profile-info">
            <img
              src={memberData?.profileImgUrl || defaultProfileImage}
              alt="User Profile"
              onError={e => {
                e.target.onerror = null;
                e.target.src = defaultProfileImage;
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
                <button className="edit-info-button">정보 수정</button>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <div className="content-container">
        <div className="calendar-section">
          <Calendar
            onChange={handleDateChange}
            value={dateClicked}
            className="react-calendar"
            calendarType="gregory"
            showNeighboringMonth={false}
            formatDay={(locale, date) => moment(date).format("D")} // 일 제거 
            formatYear={(locale, date) => moment(date).format("YYYY")} // 네비게이션 눌렀을때 숫자 년도만 보이게
            formatMonthYear={(locale, date) => moment(date).format("YYYY. MM")}
            next2Label={null}
            prev2Label={null}
            minDetail="year"
            tileContent={({ date, view }) => {
              if (view === 'month') {
                  const hasEvent = events.some(event => {
                      
                      const eventDate = new Date(event.date);
                      console.log(eventDate);
                      return eventDate.getFullYear() === date.getFullYear() &&
                             eventDate.getMonth() === date.getMonth() &&
                             eventDate.getDate() === date.getDate();
                  });
          
                  return hasEvent ? <div className='dot-container'> <div className="dot"></div></div> : null;
              }
              return null; 
          }}
          
          
          />

        </div>

      <div className="history-section">
        {conversationList.length > 0 && (
          <>
            <h2>Conversation History</h2>
            <div className="history-cards">
              {conversationList.map((chatRoom, index) => (
                <div key={index} className="history-card">
                  <div onClick={() => handleCardClick(chatRoom)}>
                    <span><strong>{new Date(chatRoom.createdTime).toLocaleDateString()}</strong></span>
                    <p>Topic: {chatRoom.topic}</p>
                    <p>Difficulty: {chatRoom.difficulty}</p>
                  </div>
                  <button className="delete-button" onClick={() => handleDeleteChatRoom(chatRoom.chatRoomId)}>Delete</button>
                </div>
              ))}
            </div>
          </>
        )}

        {quizList.length > 0 && (
          <>
            <h2>Quiz History</h2>
            <div className="history-cards">
              {quizList.map((chatRoom, index) => (
                <div key={index} className="history-card">
                  <div onClick={() => handleCardClick(chatRoom)}>
                    <span><strong>{new Date(chatRoom.createdTime).toLocaleDateString()}</strong></span>
                    <p>Difficulty: {chatRoom.difficulty}</p>
                  </div>
                  <button className="delete-button" onClick={() => handleDeleteChatRoom(chatRoom.chatRoomId)}>Delete</button>
                </div>
              ))}
            </div>
          </>
        )}

        {conversationList.length === 0 && quizList.length === 0 && (
          <p>No history found.</p>
        )}
      </div>

      <Modal show={showModal} onClose={handleCloseModal}>
  {selectedHistory && (
    <>
      <p></p>
      <p><strong>📆 Date:</strong> {new Date(selectedHistory.createdTime).toLocaleDateString()}</p>
      <p><strong>📝 Topic: </strong> {selectedHistory.topic && selectedHistory.topic.trim() !== '' ? selectedHistory.topic : 'Quiz'}</p>
      <p><strong>🎯 Difficulty:</strong> {selectedHistory.difficulty}</p>
      <p><strong>✅ Status:</strong> {selectedHistory.queryResult ? 'Completed' : 'Incomplete'}</p>
      <p><strong>💬 Chat Messages:</strong></p>
      {chatMessages.length > 0 ? (
        (() => {
          let userMessageIndex = 0; // Index for alternating questions and answers

          return chatMessages.map((message, index) => {
            let label = '';

            // Check if the topic is a quiz to alternate labels
            if (selectedHistory.topic !== 'movie' && selectedHistory.topic !== 'hamburger' && selectedHistory.topic !== 'coffee' && selectedHistory.topic !== 'travel' && selectedHistory.topic !== 'music' & selectedHistory.topic !== 'meeting' ) {
              <p>selectedHistory.topic</p>
              if (message.senderId !== 'AI') {
                // Alternate between Question and Answer for user messages
                label = userMessageIndex % 2 === 0 ? 'Question' : 'Answer';
                userMessageIndex++; // Increment only for user messages
              } else {
                label = ''; // Don't display label for AI messages yet
              }
            } else {
              // For non-quiz messages, display as 'You' or 'AI'
              label = message.senderId === 'AI' ? 'AI' : 'You';
            }


            return (
              <div key={index} className="message-item">
                {label && (
                  <h3>
                    <strong>{label}:</strong> 
                  </h3>
                )}
                {message.senderId === 'AI' && !label && message.messageText !== '' && (selectedHistory.topic === 'movie' || selectedHistory.topic === 'hamburger' || selectedHistory.topic === 'coffee' || selectedHistory.topic === 'travel' || selectedHistory.topic === 'music' || selectedHistory.topic === 'meeting') && (
                  <h3>
                    <strong>AI:</strong> 
                  </h3>
                )}
                <h3>{message.messageText}</h3>
                {message.messageText === '' && (
                  <>
                    <h4 style={{ color: 'gray' }}>
                      <em>{new Date(message.messageTime).toLocaleTimeString()}</em>
                    </h4>
                  </>
                )}
                {message.AudioFileUrl && (
                  <p>
                    <audio controls>
                      <source src={message.AudioFileUrl} type="audio/mp3" />
                      Your browser does not support the audio element.
                    </audio>
                  </p>
                )}
                {message.feedback && (
  <div>
    <p><strong>Feedback:</strong></p>
    {message.feedback.split('\n').map((line, index) => (
      <p key={index}>{line}</p>
    ))}
  </div>
)}

                <p></p>
              </div>
            );
          });
        })()
      ) : (
        <p>No messages found.</p>
      )}
    </>
  )}
</Modal>

    </div>
    </div>
  );
}

export default MyPage;
