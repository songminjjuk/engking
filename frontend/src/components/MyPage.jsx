import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import profileImage from '../assets/img/민석.jpg';
import Modal from './Modal';  // Import the Modal component
import axios from 'axios';   // Import axios for HTTP requests

function MyPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [memberData, setMemberData] = useState(null);  // State for storing member data

  // Function to fetch member data
  const fetchMemberData = async () => {
    try {
      const response = await axios.get('https://cors-anywhere.herokuapp.com/http://www.rapapa.site:8080/member/login');  // Fetch member data from API
      setMemberData(response.data);
    } catch (error) {
      console.error('Error fetching member data:', error);
    }
  };

  // Fetch member data when component mounts
  useEffect(() => {
    fetchMemberData();
  }, []);

  const handleCardClick = (history) => {
    setSelectedHistory(history);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedHistory(null);
  };

  return (
    <div className="my-page-container">
      {/* Profile Section */}
      <div className="profile-section">
        <button className="mypage-button">MyPage</button>
        <div className="profile-info">
          <img src={profileImage} alt="Profile" className="profile-image" />
          <div className="profile-details">
            {memberData ? (
              <>
                <div>
                  <strong>Name</strong> <span>{memberData.name}</span>
                </div>
                {/* <div>
                  <strong>Level</strong> <span>{memberData.authority}</span> {/* Assuming authority represents level */}
                {/* </div>
                <div>
                  <strong>Ranking</strong> <span>{memberData.ranking || 'N/A'}</span> {/* If ranking is available */}
                {/* </div> */} 
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
        <h2>Conversation History</h2>
        <div className="history-cards">
          <div className="history-card" onClick={() => handleCardClick({ date: '2024.08.13', score: 200 })}>
            <span>2024.08.13</span>
            <p>score : {200}</p> {/* Use a variable for score */}
          </div>
          {/* Add more cards as needed */}
        </div>

        <h2>Quiz History</h2>
        <div className="history-cards">
          <div className="history-card" onClick={() => handleCardClick({ date: '2024.08.13', score: 1022 })}>
            <span>2024.08.13</span>
            <p>score : {1022}</p> {/* Use a variable for score */}
          </div>
          {/* Add more cards as needed */}
        </div>
      </div>

      {/* Modal for detailed history view */}
      <Modal show={showModal} onClose={handleCloseModal}>
        {selectedHistory && (
          <>
            <h3 style={{ fontWeight: 700 }}>{selectedHistory.date}</h3>
            <p><strong>📆 날짜:</strong> {selectedHistory.date}</p>
            <p><strong>🥇 점수:</strong> {selectedHistory.score}</p>
            <p><strong>✅ 상세 내용</strong></p>
            <p>단어를 어쩌구저쩌구로 바꾸면 좋을 듯 ?</p>
            <p>맥락에 맞지 않다는 둥 어쩌구 저쩌구</p>
            <p>어쩌구 저쩌구 블라블라</p>
            {/* Add more detailed information as needed */}
          </>
        )}
      </Modal>
    </div>
  );
}

export default MyPage;
