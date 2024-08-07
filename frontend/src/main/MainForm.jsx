import React, { useRef, useEffect, useContext, useState } from 'react';
import { Link } from 'react-router-dom';
import { SEOMetaTag } from '../snippets';
import Post from './PostForm';

function MainForm() {
    const [posts, setPosts] = useState([]);
    useEffect(() => {
        //api호출 axios 넣어야됨
    }, []);

    return (
        <div className='main-container'>
            <SEOMetaTag 
                title='챠우챠우'
                description='동물들과 대화해보세요'
                keywords='유기동물, 유기견, sns, 동물sns, 챠우챠우'
                //image='https://미정/og_image.png'
                //url='https://미정'
            />
            <main className='feed'>
                {!posts.length && <p>게시물이 없습니다.</p>}
                {posts.map(post => (
                    <Post key={post.id} post={post} />
                ))}
            </main>
        </div>
    );
}

export default MainForm;
