import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Header from './components/Header';
import Main from './components/Main';
import Footer from './components/Footer';
import Slider from './components/Slider';
import Image from './components/Image';
import Member from './components/Member';

import AboutPage from './components/AboutPage';
import TitlePage from './components/TitlePage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import MyPage from './components/MyPage';
import EditInfoPage from './components/EditInfoPage';
import StartPage from './components/ConversationPage';
import Conversation from './components/Conversation';
import QuizPage from './components/QuizPage';
import QuizDifficultyPage from './components/QuizDifficultyPage';
import QuizTitle from './components/QuizTitlePage';
import ConvResultPage from './components/ConvResultPage';
import QuizResultPage from './components/QuizResultPage';
import PrivateRoute from './components/PrivateRoute';

import './assets/css/reset.css';
import './assets/css/style.css';

const App = () => {
  const [email, setEmail] = useState('');
  const [userId, setUserId] = useState('');
  const [reload, setReload] = useState(false);

  useEffect(() => {
    const storedEmail = localStorage.getItem('email');
    const storedUserId = localStorage.getItem('userId');
    if (storedEmail) {
      setEmail(storedEmail);
    } else {
      setEmail('');
    }

    if (storedUserId) {
      setUserId(storedUserId);
    } else {
      setUserId('');
    }
  }, [reload]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    setEmail('');
  };

  const isLoggedIn = !!email;

  return (
    <BrowserRouter>
      <Header email={email} setEmail={setEmail} />

      <Main>
        <Routes>
          <Route 
            path="/" 
            element={
              <>
                <Slider element="nexon" />
                <Image element="section nexon" title="Introduction" />
                <Member element="section nexon" title="Team Member" />
              </>
            } 
          />
          <Route path="/title" element={<TitlePage />} />
          <Route path="/login" element={<LoginPage reload={reload} setReload={setReload} />} />
          <Route path="/SignUp" element={<RegisterPage />} />
          <Route path="/mypage" element={<MyPage />} />
          <Route path="/edit-info" element={<EditInfoPage />} />
          <Route path="/start" element={<StartPage />} />
          <Route path="/conversation" element={<Conversation />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/quiztitle" element={<QuizTitle />} />
          <Route path="/quizresult" element={<QuizResultPage />} />
          <Route path="/convresult" element={<ConvResultPage />} />

          {/* Protected routes */}
          <Route 
            path="/about" 
            element={<PrivateRoute element={<AboutPage />} isLoggedIn={isLoggedIn} />} 
          />
          <Route 
            path="/quizdiffi" 
            element={<PrivateRoute element={<QuizDifficultyPage />} isLoggedIn={isLoggedIn} />} 
          />
        </Routes>
      </Main>

      <Footer element="nexon section gray" />
    </BrowserRouter>
  );
};

export default App;
