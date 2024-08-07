import React, { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './community.css';
import pencil from '../static/img/pen.png';
import view from '../static/img/view.png';
import comment from '../static/img/comment.png';
import { OnlineUser } from '../snippets';
import { UserContext } from '../UserContext';
import { SEOMetaTag } from '../snippets';

function CMainForm() {
    const [posts, setPosts] = useState([]);
    const [selectedType, setSelectedType] = useState('');
    const { user } = useContext(UserContext);
    //인피니트 스크롤
    const [offset, setOffset] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const limit = 10;
    //화면너비
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);
    // 화면 너비 감지 및 업데이트
    useEffect(() => {
        const handleResize = () => {
            setWindowWidth(window.innerWidth);
        };
        window.addEventListener('resize', handleResize);
        // 컴포넌트가 언마운트 될 때 이벤트 리스너 제거
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
        // 선택된 type 변경 시 초기 게시물 로드
        setPosts([]); // 게시물 목록 초기화
        setOffset(0); // 오프셋 초기화
        setHasMore(true); // 더 로드할 게시물이 있다고 가정
        fetchInitialPosts(); // 초기 게시물 로드
    }, [selectedType]);

    useEffect(() => {
        const handleScroll = () => {
            if (window.innerHeight + document.documentElement.scrollTop + 1 >= document.documentElement.scrollHeight && !isLoading && hasMore) {
                fetchMorePosts();
            }
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [isLoading, hasMore, selectedType, offset]);

    const fetchInitialPosts = async () => {
        setIsLoading(true);
        const url = `/api/community/posts/${selectedType ? `?type=${selectedType}&limit=${limit}&offset=0` : `?limit=${limit}&offset=0`}`;
        try {
            const response = await axios.get(url);
            setPosts(response.data.results); // 데이터 구조에 따라 response.data 혹은 response.data.posts 등으로 조정 필요
            setOffset(response.data.results.length);
            setHasMore(!!response.data.next); // 데이터 구조에 따라 조정 필요
            setIsLoading(false);
        } catch (error) {
            console.error(error);
            setIsLoading(false);
        }
    };

    const fetchMorePosts = async () => {
        setIsLoading(true);
        const url = `/api/community/posts/${selectedType ? `?type=${selectedType}&limit=${limit}&offset=${offset}` : `?limit=${limit}&offset=${offset}`}`;
        try {
            const response = await axios.get(url);
            setPosts(prev => [...prev, ...response.data.results]); // 데이터 구조에 따라 조정 필요
            setOffset(prevOffset => prevOffset + response.data.results.length); // 데이터 구조에 따라 조정 필요
            setIsLoading(false);
            setHasMore(!!response.data.next); // 데이터 구조에 따라 조정 필요
        } catch (error) {
            console.error(error);
            setIsLoading(false);
        }
    };

    const truncate = (str, n) => {
        return str?.length > n ? str.substr(0, n - 1) + "..." : str;
    };
    // 조건적 truncate
    const conditionalTruncate = (str) => {
        if (windowWidth <= 400) {
            return truncate(str, 25);
        } else if (windowWidth <= 530) {
            return truncate(str, 35);
        } else if (windowWidth <= 650) {
            return truncate(str, 45);
        } else if (windowWidth <= 768) {
            return truncate(str, 55);
        } else {
            return truncate(str, 65);
        }
    };

    return (
        <div className='commu-container'>
            <SEOMetaTag 
                title='몽글몽글: 커뮤니티'
                description='대학생 커뮤니티 몽글몽글에서 다른 학교의 친구들을 만나보세요'
                keywords='몽글몽글, mongle, 랜덤채팅, 커뮤니티, mongles.com'
                image='https://mongles.com/og_image.png'
                url='https://mongles.com/community/'
            />
            <Link to="/community/create" className="commu-container__create-link">
                <img src={pencil} alt="Pencil"></img>
                <span> 글쓰기</span>
            </Link>
            <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)} className="type-select">
                <option value="">통합 게시판</option>
                <option value="0">랜덤채팅</option>
                <option value="1">썸/연애</option>
                <option value="2">주식/투자</option>
                <option value="3">재수/반수/편입</option>
                <option value="4">취업/창업</option>
                <option value="5">여행/먹방</option>
                <option value="6">게임</option>
                <option value="7">패션/뷰티</option>
                <option value="8">유머</option>
                <option value="9">군대</option>
                <option value="10">팀원모집/프로젝트</option>
                <option value="11">만화/애니/영화</option>
                <option value="12">일상</option>
                <option value="13">연예인</option>
                <option value="14">인생 꿀팁</option>
            </select>
            {/*<p className='online-user'>접속자: {onlineUser}명</p>*/}
            {user&&<OnlineUser/>}
            <div className='total'>
                {posts.length > 0 ? (
                    <ul className="commu-container__post-list">
                        {posts.map((post) => (
                            <li key={post.id} className="commu-container__post-list-item">
                                <Link to={`/community/posts/${post.id}`} className="commu-container__post-link">
                                    <p className='commu-container__post-list-item-type'>{post.type_display}</p>
                                    <p className='commu-container__post-list-item-title'>{conditionalTruncate(post.title)}</p>
                                    <p className='commu-container__post-list-item-content'>{conditionalTruncate(post.content)}</p>
                                </Link>
                                <div className='commu-container__post-list-item-i'>
                                    <div className='commu-container__post-list-item-i-view'>
                                        <img src={view} alt="view" />
                                        <p>{post.view_count}</p>
                                    </div>
                                    <div className='commu-container__post-list-item-i-comment'>
                                        <img src={comment} alt="view" />
                                        <p>{post.comments_count}</p>
                                    </div>
                                </div>
                                <div className='date-school'>
                                    <p className='commu-container__post-list-item-date'>{formatDate(post.created_at)}</p>
                                    <p className='commu-container__post-list-item-date-school'>- {post.user.username === 'jeff721' ? '관리자 ★' : post.user.school_name}</p>
                                </div>  
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>등록된 게시물이 없습니다</p>
                )}
            </div>
        </div>
    );
}

export default CMainForm;
