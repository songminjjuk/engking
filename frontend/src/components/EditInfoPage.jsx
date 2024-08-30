import React, { useState, useEffect } from 'react';
import axios from 'axios';

function EditInfoPage() {
  const [name, setName] = useState('뿡순');
  const [number, setNumber] = useState('010-0000-0000');
  const [birth, setBirth] = useState('0000-00-00');
  const [userId, setUserId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user data on component mount
  useEffect(() => {
    const storedUserId = localStorage.getItem('userId'); // Retrieve userId from localStorage
    const email = localStorage.getItem('email'); // Example: Adjust this based on how you store the email

    if (storedUserId) {
      setUserId(storedUserId);

      // Optionally fetch user data to populate fields
      const fetchUserData = async () => {
         try {
           const response = await axios.get('http://www.rapapa.site:8080/member/info', {
            params: { email: email }// Authentication headers are removed as we're not using tokens
           });

           // Set state with fetched user data
           setName(response.data.name || '');
           setNumber(response.data.phone || '');
           setBirth(response.data.birthday || '');
         } catch (error) {
           console.error('Error fetching user data:', error);
         } finally {
           setIsLoading(false);
         }
       };

       fetchUserData();
    } else {
       setUserId(null);
       setIsLoading(false);
     }
  }, []);

  const handleSave = () => {
    // Logic for saving updated info
    alert('Information saved!');
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        try {
            const storedUserId = localStorage.getItem('userId');
            if (!storedUserId) {
                throw new Error('User ID is missing.');
            }

            // Making the DELETE request with the data in the body
            const response = await axios.delete('https://cors-anywhere.herokuapp.com/http://www.rapapa.site:8080/member/delete', {
                headers: {
                    'Content-Type': 'application/json',
                },
                data: {
                    id: Number(storedUserId)
                }
            });

            if (response.status === 204) {
                alert('Account successfully deleted!');
                localStorage.removeItem('userId');
                setUserId(null);
                window.location.href = '/login';  // Redirect to login or another page
            } else {
                throw new Error('Failed to delete account');
            }
        } catch (error) {
            console.error('There was a problem with the delete operation:', error);

            if (error.response && error.response.status === 403) {
                alert('Permission denied. You might not be authorized to delete this account.');
            } else {
                alert('An error occurred while deleting your account. Please try again later.');
            }
        }
    }
};

  

  // if (isLoading) {
  //   return <div>Loading...</div>; // Display loading indicator while fetching user data
  // }

  return (
    <div className="edit-info-container">
      <div className="edit-info-section">
        <h2>Edit Member Information</h2>
        <div className="edit-info-form">
          <div className="form-field">
            <label>Name:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label>전화번호</label>
            <input
              type="text"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label>생년월일</label>
            <input
              type="text"
              value={birth}
              onChange={(e) => setBirth(e.target.value)}
            />
          </div>
          <button onClick={handleSave} className="save-button">
            Save
          </button>
          <button onClick={handleDelete} className="delete-button">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}

export default EditInfoPage;
