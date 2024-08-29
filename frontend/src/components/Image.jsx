import React from 'react'

const Image = ( props ) => {
    return (
        <section id="imageType" className={`imageType__wrap ${props.element}`}>
            <h2>{props.title}</h2>
            <p>AI 기반 영어 회화 연습 서비스</p>
            <div className="image__inner container">
                <article className="image img1">
                    <h3 className="image__title">영어 회화 연습</h3>
                    <p className="image__desc">AI와 함께 회화 연습을 !</p>
                    <a className="image__btn" href="/about">하러 가기</a>
                </article>
                <article className="image img2">
                    <h3 className="image__title">영어 / 문법 퀴즈</h3>
                    <p className="image__desc">AI와 함께 퀴즈를 !</p>
                    <a className="image__btn yellow" href="/quizdiffi">하러 가기</a>
                </article>
            </div>
        </section>
    )
}

export default Image