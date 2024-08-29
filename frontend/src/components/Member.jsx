import React from 'react'

const Member = ( props ) => {
    return (
        <section id="imageType" className={`imageType__wrap ${props.element}`}>
            <h2>{props.title}</h2>
            <p>이쿠조</p>
            <div className="image__inner container">
                <article className="image m1">
                    <h3 className="member__title">곽재형</h3>
                    <p className="member__desc">백엔드</p>
                </article>
                <article className="image m2">
                    <h3 className="member__title">박선영</h3>
                    <p className="member__desc">백엔드</p>
                </article>
                <article className="image m3">
                    <h3 className="member__title">송민석</h3>
                    <p className="member__desc">AI</p>
                </article>
                <article className="image m4">
                    <h3 className="member__title">정남헌</h3>
                    <p className="member__desc">백엔드</p>
                </article>
                <article className="image m5">
                    <h3 className="member__title">한수빈</h3>
                    <p className="member__desc">프론트</p>
                </article>
            </div>
        </section>
    )
}

export default Member;