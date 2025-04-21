import React from 'react';
import banner from '../assets/img/infobanner.png'; // 가로로 긴 이미지
import monitor from '../assets/img/engking-monitor.png';
import engking from '../assets/img/engking.png';
import wordImage from '../assets/img/word-icon.png'; // 단어 섹션 이미지
import grammarImage from '../assets/img/grammar-icon.png'; // 문법 섹션 이미지
import bbanner from '../assets/img/bbanner.png'
const Info = (props) => {
  return (
    <div className="info-container">
      {/* Banner section with image and text */}
      <div className="banner">
        <img src={monitor} alt="Service Banner" className="banner-image" />
        <div className="banner-text">
          <img src={engking} className="logo" alt="Engking Logo" />
          <p></p>
        </div>
      </div>

      {/* Vertically centered content */}
      <div className="text-container">
        {/* 가로로 긴 이미지 */}


        {/* Service Introduction Section */}
        <section className="getting-started">
  
          <h2>영어 회화를 습관처럼 !</h2>
          <ol className="start-steps">
          <li>언제 어디서나 접속만 하면 바로 연습할 수 있어요</li>
          <p>실시간으로 영어 회화를 연습할 수 있어요</p> 
          <p>문법, 어휘에 대한 피드백을 제공해요</p>
          </ol>
        </section>

        {/* Getting Started Section */}
        <section className="getting-started">
        <div className="wide-banner">
          <img src={bbanner} alt="Wide Banner" className="wide-banner-image" />
        </div>
          <h2>혼자 할 수 있는 회화 연습 !</h2>
          <ol className="start-steps">
            <li>독해, 리스닝은 혼자 할 수 있지만 회화는 혼자 못해요</li>
            <li>함께 회화 연습할 상대를 찾기도 힘들어요</li>
            <li>원어민과 영어로 이야기할 기회가 없어요</li>
            <li>잉킹으로는 해결할 수 있어요</li>
            <li><strong>지금 바로 잉킹으로 시작하세요 !</strong></li>
          </ol>
        </section>

        {/* Key Features Section */}
        <section className="key-features">
          <h2>퀴즈를 통해 영어 실력을 향상시켜요</h2>
          <div className="feature-item">
            <img src={wordImage} alt="Word Quiz Icon" className="feature-icon" />
            <div className="feature-text">
              <ul className="features-list">
                <li><strong>단어</strong></li>
                <li>게임하듯 단어 퀴즈를 풀어보아요</li>
                <li>난이도도 선택할 수 있어요 !</li>
                <li>다양한 예문으로 활용력까지 챙길 수 있어요 !</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="key-features">
          <h2></h2>
          <div className="feature-item">
            <img src={grammarImage} alt="Grammar Quiz Icon" className="feature-icon" />
            <div className="feature-text">
              <ul className="features-list">
                <li><strong>문법</strong></li>
                <li>문법 퀴즈를 통해 문법을 탄탄히 해요 !</li>
                <li>난이도도 선택할 수 있어요 !</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Info;
