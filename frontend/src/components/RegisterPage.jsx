import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const SignUp = () => {
  const navigate = useNavigate();

  // State to manage form data
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    birthdate: '',
    terms: false,
  });

  // State to manage error messages
  const [errorMessage, setErrorMessage] = useState('');

  // Handler for form input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  // Handler for form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
  
    if (!formData.terms) {
      setErrorMessage('You must agree to the terms and conditions.');
      return;
    }
  
    try {
      // 프록시 설정을 고려하여 상대 경로로 요청
      const response = await axios.post('http://www.rapapa.site:8080/member/register', {
        email: formData.email,
        password: formData.password,
        name: formData.name,
        phone: formData.phone,
        birthday: formData.birthdate, // 서버가 'birthday' 필드를 기대하는 경우
      });
  
      // Handle successful response
      console.log('Success:', response.data);
      navigate('/Login'); // Redirect to login page on success
    } catch (error) {
      // Handle error response
      if (error.response && error.response.data) {
        setErrorMessage(error.response.data.message || 'Failed to register. Please try again.');
      } else {
        setErrorMessage('There was an error with the registration.');
      }
      console.error('Error:', error);
    }
  };

  // Navigate to SignIn page
  const goToSignIn = () => {
    navigate('/Login');
  };

  return (
    <div id="form-container">
      <div id="form-inner-container">
        <div id="sign-up-container">
          <h3 className="login-text">Get Started</h3>
          <form onSubmit={handleSubmit}>
            {errorMessage && <div className="error-message">{errorMessage}</div>}
            
            <label htmlFor="name">Name</label>
            <input
              type="text"
              name="name"
              id="name"
              placeholder="Name"
              value={formData.name}
              onChange={handleChange}
              required
            />

            <label htmlFor="email">Email</label>
            <input
              type="email"
              name="email"
              id="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
            />

            <label htmlFor="password">Password</label>
            <input
              type="password"
              name="password"
              id="password"
              placeholder="&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;"
              value={formData.password}
              onChange={handleChange}
              required
            />

            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              name="phone"
              id="phone"
              placeholder="Phone Number"
              value={formData.phone}
              onChange={handleChange}
              pattern="[0-9]{11}" // Optional: pattern for phone number validation
              required
            />

            <label htmlFor="birthdate">Date of Birth</label>
            <input
              type="date"
              name="birthdate"
              id="birthdate"
              placeholder="YYYY-MM-DD"
              value={formData.birthdate}
              onChange={handleChange}
              required
            />

            <div id="form-controls">
              <button type="submit" onClick={handleSubmit}>Sign Up</button>
              <button type="button" onClick={goToSignIn}>Sign In</button>
            </div>

            <input
              type="checkbox"
              name="terms"
              id="terms"
              checked={formData.terms}
              onChange={handleChange}
            />
            <label htmlFor="terms">
              I agree to the{' '}
              <a href="#" className="termsLink">Terms of service</a> and{' '}
              <a href="#" className="termsLink">Privacy Policy</a>.
            </label>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
