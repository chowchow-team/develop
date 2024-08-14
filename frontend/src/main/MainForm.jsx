import React, { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './main.css';
import pencil from '../static/img/pen.png';
import { UserContext } from '../UserContext';
import { SEOMetaTag } from '../snippets';
import PostForm from './PostForm';

function MainForm() {
    const [posts, setPosts] = useState([]);
    const { user } = useContext(UserContext);
    const [offset, setOffset] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const limit = 10;
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);
    const [activeTab, setActiveTab] = useState('recommend');
    

    useEffect(() => {
        const handleResize = () => setWindowWidth(window.innerWidth);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const formatDate = (dateStr) => {
        const postDate = new Date(dateStr);
        const now = new Date();
        const diffSeconds = Math.round((now - postDate) / 1000);
        const diffMinutes = Math.round(diffSeconds / 60);
        const diffHours = Math.round(diffMinutes / 60);
        const diffDays = Math.round(diffHours / 24);
        const diffMonths = Math.round(diffDays / 30);
        const diffYears = Math.round(diffMonths / 12);

        if (diffSeconds < 60) {
            return `${diffSeconds}초 전`;
        } else if (diffMinutes < 60) {
            return `${diffMinutes}분 전`;
        } else if (diffHours < 24) {
            return `${diffHours}시간 전`;
        } else if (diffDays < 30) {
            return `${diffDays}일 전`;
        } else if (diffMonths < 12) {
            return `${diffMonths}달 전`;
        } else {
            return `${diffYears}년 전`;
        }
    };

    useEffect(() => {
        setPosts([]);
        setOffset(0);
        setHasMore(true);
        fetchInitialPosts();
    }, [activeTab]);

    useEffect(() => {
        const handleScroll = () => {
            if (
                window.innerHeight + document.documentElement.scrollTop + 1 >=
                document.documentElement.scrollHeight &&
                !isLoading &&
                hasMore
            ) {
                fetchMorePosts();
            }
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [isLoading, hasMore, offset]);

    const fetchInitialPosts = async () => {
        setIsLoading(true);
        try {
            const addr = activeTab === 'recommend' ? '/api/main/' : '/api/main/post/follow/';
            const response = await axios.get(`${addr}?limit=${limit}&offset=0`);
            setPosts(response.data.results);
            setOffset(response.data.results.length);
            setHasMore(!!response.data.next);
            setIsLoading(false);
        } catch (error) {
            setIsLoading(false);
        }
    };

    const fetchMorePosts = async () => {
        setIsLoading(true);
        try {
            const response = await axios.get(`/api/main/?limit=${limit}&offset=${offset}`);
            setPosts(prev => [...prev, ...response.data.results]);
            setOffset(prevOffset => prevOffset + response.data.results.length);
            setHasMore(!!response.data.next);
            setIsLoading(false);
        } catch (error) {
            alert('게시물을 불러오는데 실패했습니다');
            setIsLoading(false);
        }
    };

    return (
        <div className='main-container'>
            <SEOMetaTag 
                title='챠우챠우'
                description='동물들과 대화해보세요'
                keywords='유기동물, 유기견, sns, 동물sns, 챠우챠우'
            />
            <Link to="/feed/posts/create" className="main-container__create-link">
                <img src={pencil} alt="Pencil" />
            </Link>
            
            <div className='total'>
                <div className='ctrl-box'>
                    <button
                        className={`recommend-btn ${activeTab === 'recommend' ? 'active' : ''}`}
                        onClick={() => setActiveTab('recommend')}
                        role="tab"
                        aria-selected={activeTab === 'recommend'}
                    >
                        추천
                    </button>
                    <button
                        className={`follow-btn ${activeTab === 'follow' ? 'active' : ''}`}
                        onClick={() => setActiveTab('follow')}
                        role="tab"
                        aria-selected={activeTab === 'follow'}
                    >
                        팔로우 중
                    </button>
                </div>
                {posts.length > 0 ? (
                    <ul className="main-container__post-list">
                        {posts.map((post) => (
                            <PostForm key={post.id} post={post} formatDate={formatDate} />
                        ))}
                    </ul>
                ) : (
                    <p>등록된 게시물이 없습니다</p>
                )}
                {isLoading && <p>로딩 중...</p>}
            </div>
        </div>
    );
}

export default MainForm;