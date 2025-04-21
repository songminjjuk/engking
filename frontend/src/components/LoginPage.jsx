import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginPage = ({ reload, setReload }) => {
  const navigate = useNavigate();

  // State to manage form data
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  // State to manage error messages
  const [errorMessage, setErrorMessage] = useState('');

  // Handler for form input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked: value,
    });
  };

  // Handler for form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.terms) {
      setErrorMessage('You must agree to the terms and conditions to log in.');
      return; // Prevent form submission if terms are not accepted
  }
    try {
      // Make API request to the login endpoint
      const response = await axios.post('https://sback.engking.site/member/login', {
        email: formData.email,
        password: formData.password,
      });
  
      // Log the entire response data
      console.log('Response Data:', response.data);
  
      // Check if user data is present
      if (response.data.email) {
        // Store user data in localStorage
        localStorage.setItem('email', response.data.email);
        localStorage.setItem('userId', response.data.id); // Use id instead of memberId
        console.log(localStorage.getItem('userId')); // Log to confirm it's stored correctly
  
        // Redirect to home page or another page
        setReload(!reload); // Update state to trigger re-render
        navigate('/'); // Redirect to home page or a protected route
      } else {
        // If no user data is received, show an error message
        console.warn('No user data received in the response:', response.data);
        setErrorMessage('Login failed. Please try again.');
      }
    } catch (error) {
      // Handle error response
      if (error.response && error.response.data) {
        setErrorMessage(error.response.data.message || 'Failed to login. Please try again.');
      } else {
        setErrorMessage('There was an error with the login request.');
      }
      console.error('Login Error:', error);
    }
  };
  
  

  return (
    <div id="form-container">
      <div id="form-inner-container"></div>
      <div id="sign-in-container">
        <h3 className="login-text">Welcome Back</h3>
        <form onSubmit={handleSubmit}>
          {errorMessage && <div className="error-message">{errorMessage}</div>}
          
          <label htmlFor="email">Email</label>
          <input
            type="email"
            name="email"
            id="email"
            placeholder="user@example.com"
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

          <div id="form-controls">
            <button type="submit">Sign In</button>
            <button type="button" onClick={() => navigate('/SignUp')}>
              Sign Up
            </button>
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
  );
};

export default LoginPage;