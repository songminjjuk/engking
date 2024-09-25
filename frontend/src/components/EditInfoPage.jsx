import React, { useState, useEffect } from 'react';
import axios from 'axios';

function EditInfoPage() {
  const [name, setName] = useState('');
  const [number, setNumber] = useState('');
  const [birth, setBirth] = useState('');
  const [userId, setUserId] = useState(null);
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [imageFile, setImageFile] = useState(null); // For storing selected image file
  const [profileImage, setProfileImage] = useState(''); // For displaying profile image
  const [imageLoaded, setImageLoaded] = useState(false); // New state to manage image loading

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    const storedEmail = localStorage.getItem('email');
  
    if (storedUserId && storedEmail) {
      setUserId(storedUserId);
      setEmail(storedEmail);
  
      const fetchUserData = async () => {
        try {
          const response = await axios.post(`http://35.72.9.14:8080/member/info?email=${storedEmail}`);
  
          console.log('Response Data:', response.data);
  
          if (response.data) {
            setName(response.data.name || '');
            setNumber(response.data.phone || '');
            setBirth(response.data.birthday || '');
            setProfileImage(response.data.profileImgUrl || '');
          } else {
            console.warn('No data returned from the API');
          }
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

  const handleSave = async () => {
    try {
      const storedUserId = localStorage.getItem('userId');
      if (storedUserId) {
        setUserId(storedUserId); // Update userId if needed
      }
  
      if (!userId) {
        throw new Error('User ID is missing.');
      }
  
      const data = {
        id: 4, // Ensure this is a valid number
        email: email,
        name: name,
        phone: number,
        birthday: birth,
      };
  
      const response = await axios.patch('http://35.72.9.14:8080/member/update', data, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
  
      if (response.status === 200) {
        const { profileImgUrl } = response.data;
        console.log('Profile updated, S3 URL:', profileImgUrl);
  
        if (profileImgUrl && imageFile) {
          await axios.put(profileImgUrl, imageFile, {
            headers: {
              'Content-Type': 'image/jpeg'
            }
          });
          alert('Profile and image updated successfully!');
        } else if (profileImgUrl) {
          alert('Profile updated successfully, but no new image was uploaded.');
        }
      } else {
        throw new Error('Failed to update information');
      }
    } catch (error) {
      console.error('Error updating information:', error);
      alert(`An error occurred: ${error.response?.statusText || error.message}`);
    }
  };
  

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        const storedUserId = localStorage.getItem('userId');
        if (!storedUserId) {
          throw new Error('User ID is missing.');
        }

        const response = await axios.delete('http://35.72.9.14:8080/member/delete', {
          headers: {
            'Content-Type': 'application/json',
          },
          data: {
            id: Number(storedUserId),
          },
        });

        if (response.status === 204) {
          alert('Account successfully deleted!');
          localStorage.removeItem('userId');
          window.location.href = '/login';
        } else {
          throw new Error('Failed to delete account');
        }
      } catch (error) {
        console.error('Error deleting account:', error);

        if (error.response && error.response.status === 403) {
          alert('Permission denied. You might not be authorized to delete this account.');
        } else {
          alert('An error occurred while deleting your account. Please try again later.');
        }
      }
    }
  };

  const handleImageChange = (e) => {
    setImageFile(e.target.files[0]);
  };

  const handleImageLoad = () => {
    setImageLoaded(true); // Set the image as loaded when it's fully rendered
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="edit-info-container">
      <div className="edit-info-section">
        <h2>회원 정보 수정</h2>
        <div className="edit-info-form">
          <div className="form-field">
            <label>이름</label>
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
              type="date"
              value={birth}
              onChange={(e) => setBirth(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label>프로필 이미지</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              style={{ backgroundColor: 'white' }}
            />
            {profileImage && (
              <div>
                <img
                  src={profileImage}
                  alt="Profile"
                  onLoad={handleImageLoad} // Call handleImageLoad when the image is loaded
                  onError={(e) => {
                    e.target.onerror = null; // Prevent infinite loop if the default image fails
                    e.target.src = null; // Set to default image on error
                  }}
                  className="profile-image-preview"
                  style={{ opacity: imageLoaded ? 1 : 0, transition: 'opacity 0.5s ease-in' }} // Smooth fade-in for the image
                />
              </div>
            )}
          </div>
          <button onClick={handleSave} className="save-button">
            저장
          </button>
          <button onClick={handleDelete} className="delete-button">
            회원 탈퇴
          </button>
        </div>
      </div>
    </div>
  );
}

export default EditInfoPage;
