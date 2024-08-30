import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';

const Header = (props) => {
  const { email, setEmail } = props;

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      const storedEmail = localStorage.getItem('email');
      if (storedEmail) {
        setEmail(storedEmail);
      }
    } else {
      setEmail('');
    }
  }, [setEmail]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    setEmail('');
  };

  return (
    <header id="headerType" className="header__wrap">
      <div className="header__inner">
        <div className="header__logo">
          <NavLink to="/">이쿠조 <em>잉킹 EngKing</em></NavLink>
        </div>
        <nav className="header__menu">
          <ul>
            <li><NavLink to="/quizdiffi">퀴즈</NavLink></li>
            <li><NavLink to="/about">회화</NavLink></li>
            {email && (
              <li><NavLink to="/mypage">MyPage</NavLink></li> 
            )}
          </ul>
        </nav>
        <div className="header__member">
          {email ? (
            <div>
              <span>{email}</span> {/* Display user email */}
              <button onClick={handleLogout} className="logout-button">Logout</button>
            </div>
          ) : (
            <NavLink to="/login">로그인</NavLink>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
