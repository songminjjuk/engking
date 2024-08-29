import React from 'react'

const Footer = ( props ) => {
    return (
        <footer id="footerType" className={`footer__wrap ${props.element}`}>
            <h2 className="blind">푸터 영역</h2>
            <div className="footer__inner container">
                <div className="footer__menu">
                    <div>
                        <h3>AWS 5기</h3>
                        <ul>
                            <li><a href="/">4조</a></li>
                            <li><a href="/">이쿠조</a></li>
                        </ul>
                    </div>
                    <div>
                        <h3>조원</h3>
                        <ul>
                            <li><a href="/">곽재형</a></li>
                            <li><a href="/">박선영</a></li>
                            <li><a href="/">송민석</a></li>
                            <li><a href="/">정남헌</a></li>
                            <li><a href='/'>한수빈</a></li>
                        </ul>
                    </div>

                    <div>
                        <h3>~10/18</h3>
                    </div>
                    <div>
                        <h3>언제 끝나 </h3>
                    </div>
                    <div>
                        <h3>집 가고 싶당</h3>
                    </div>
                    <div>
                        <h3>푸항항항 ~ 🥱</h3>
                    </div>
                </div> 
                <div className="footer__right">
                    2024 AWS 5기 이쿠조<br />All rights reserved.
                </div>
            </div>
        </footer>
    )
}

export default Footer