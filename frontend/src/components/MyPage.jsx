import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import profileImage from '../assets/img/민석.jpg'; // Default profile image
import Modal from './Modal'; // Import the Modal component
import axios from 'axios'; // Import axios for HTTP requests

function MyPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [memberData, setMemberData] = useState(null); // State for storing member data

  // Get email from localStorage or any other source
  const email = localStorage.getItem('email'); // Example: Adjust this based on how you store the email

  // Function to fetch member data
  const fetchMemberData = async () => {
    try {
      if (email) {
        const response = await axios.get('http://www.rapapa.site:8080/member/info', {
          params: { email: email } // Send email as a query parameter
        });
        
        // Log the response to ensure it's what you expect
        console.log('API Response:', response.data);
        
        setMemberData(response.data);
      } else {
        console.error('Email is missing.');
      }
    } catch (error) {
      console.error('Error fetching member data:', error);
    }
  };

  // Fetch member data when component mounts
  useEffect(() => {
    fetchMemberData();
  }, []); // Empty dependency array means this runs once after initial render

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
          <img
            // src={memberData?.profileImgUrl || profileImage}
            src = {profileImage}
            alt="Profile"
            className="profile-image"
          />
          <div className="profile-details">
            {memberData ? (
              <>
                <div>
                  <strong>Name:</strong> <span>{memberData.name}</span>
                </div>
                <div>
                  <strong>Phone:</strong> <span>{memberData.phone || 'N/A'}</span>
                </div>
                <div>
                  <strong>Birthday:</strong> <span>{memberData.birthday || 'N/A'}</span>
                </div>
                <div>
                  <strong>Email:</strong> <span>{memberData.email}</span>
                </div>
              </>
            ) : (
              <p>Loading profile...</p>
            )}
            <Link to="/edit-info">
              <button className="edit-info-button">
                Edit Info
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
            <p>Score: {200}</p> {/* Use a variable for score */}
          </div>
          {/* Add more cards as needed */}
        </div>

        <h2>Quiz History</h2>
        <div className="history-cards">
          <div className="history-card" onClick={() => handleCardClick({ date: '2024.08.13', score: 1022 })}>
            <span>2024.08.13</span>
            <p>Score: {1022}</p> {/* Use a variable for score */}
          </div>
          {/* Add more cards as needed */}
        </div>
      </div>

      {/* Modal for detailed history view */}
      <Modal show={showModal} onClose={handleCloseModal}>
        {selectedHistory && (
          <>
            <h3 style={{ fontWeight: 700 }}>{selectedHistory.date}</h3>
            <p><strong>📆 Date:</strong> {selectedHistory.date}</p>
            <p><strong>🥇 Score:</strong> {selectedHistory.score}</p>
            <p><strong>✅ Details:</strong></p>
            <p>Details about the history item.</p>
            {/* Add more detailed information as needed */}
          </>
        )}
      </Modal>
    </div>
  );
}

export default MyPage;
