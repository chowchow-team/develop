import React, { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './main.css';
import pencil from '../static/img/pen.png';
import comment from '../static/img/comment.png';
import { UserContext } from '../UserContext';
import { SEOMetaTag } from '../snippets';


const TruncateText = ({ text, maxLength = 100 }) => {
    const [isExpanded, setIsExpanded] = useState(false);
  
    const toggleExpand = (e) => {
        e.preventDefault();  // 링크 이벤트 중지
        e.stopPropagation(); // 이벤트 버블링 방지용 (더보기떄문에 추가함)
      setIsExpanded(!isExpanded);
    };
  
    return (
      <div className="truncate-text">
        <p>
          {isExpanded ? text : `${text.slice(0, maxLength)}${text.length > maxLength ? '...' : ''}`}
        </p>
        {text.length > maxLength && (
          <button onClick={toggleExpand} className="truncate-text__button">
            {isExpanded ? '접기' : '더보기'}
          </button>
        )}
      </div>
    );
};

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
            console.error(error);
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
            console.error(error);
            setIsLoading(false);
        }
    };

    const truncate = (str, n) => {
        return str?.length > n ? str.substr(0, n - 1) + "..." : str;
    };

    const conditionalTruncate = (str) => {
        if (windowWidth <= 400) return truncate(str, 25);
        if (windowWidth <= 530) return truncate(str, 35);
        if (windowWidth <= 650) return truncate(str, 45);
        if (windowWidth <= 768) return truncate(str, 55);
        return truncate(str, 65);
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
                            <Link to={`/feed/posts/${post.id}`} className="main-container__post-link">
                            <li key={post.id} className="main-container__post-list-item">
                                <div className='main-container__post-list-item-profile'>
                                    <img src={post.user.profile_pic} alt="" />
                                    <div className='main-container__post-list-item-profile-name'>
                                        <p className='nickname'>{post.user.nickname}</p>
                                        <p className='username'>@{post.user.username}</p>
                                    </div>
                                </div>
                                <div className='main-container__post-list-item-inner'>
                                <p className='main-container__post-list-item-content'>
                                    <TruncateText text={post.content} maxLength={200} />
                                </p>
                                <p>{post.user.nickname}</p>
                                {post.images && post.images.length > 0 && (
                                    <div className={`main-container__post-list-item-images images-count-${post.images.length}`}>
                                        {post.images.slice(0, 4).map((image, index) => (
                                            <div key={index} className="image-wrapper">
                                                <img 
                                                    src={image.image} 
                                                    alt={`Post image ${index + 1}`} 
                                                    className="main-container__post-list-item-image"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                )}
                                
                                <div className='main-container__post-list-item-i'>
                                    <div className='main-container__post-list-item-i-comment'>
                                        <img src={comment} alt="comment" />
                                        <p>{post.comments_count}</p>
                                    </div>
                                </div>
                                <div className='date-school'>
                                    <p className='main-container__post-list-item-date'>{formatDate(post.timestamp)}</p>
                                </div>
                                </div>
                            </li>
                            </Link>
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