import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import defaultImg from '../static/img/logo.png';
import { URLManagement, getCookie } from '../snippets';
import PostForm from '../main/PostForm';

import './profile.css';

function ProfileDetailForm() {
    const [profile, setProfile] = useState({
        nickname: '',
        bio: '',
        profilePic: '',
        profilePicPreview: '',
        followers_count: 0,
        following_count: 0,
    });

    const { user, getUserId } = useContext(UserContext);
    const navigate = useNavigate();
    const { username } = useParams();
    const API_BASE_URL = URLManagement('http');

    const [activeTab, setActiveTab] = useState('mypost');
    const [posts, setPosts] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isFollowing, setFollowing] = useState(null);

    const isOwnProfile = user && user.username === username;
    const userid= getUserId();
    useEffect(() => {
        fetchProfile();
    }, [user, navigate, username, isFollowing]);

    useEffect(() => {
        setPosts([]);
        fetchPosts();
    }, [activeTab, username]);

    const fetchProfile = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/profile/${username}/`, {
                withCredentials: true
            });
            setProfile(response.data);
            console.log(profile);
        } catch (error) {
            console.error('프로필 정보를 불러오는데 실패했습니다', error);
        }
    };

    const fetchPosts = async () => {
        setIsLoading(true);
        try {
            let response;
            if (activeTab === 'mypost') {
                response = await axios.get(`${API_BASE_URL}/api/main/post/${username}/`, {
                    withCredentials: true
                });
                setPosts(response.data.results);  // mypost의 경우 results 배열을 저장
            } else if (activeTab === 'like') {
                response = await axios.get(`${API_BASE_URL}/api/main/liked-posts/`, {
                    withCredentials: true
                });
                setPosts(response.data);  // like의 경우 바로 데이터를 저장
            }
            
            console.log('Fetched posts:', response.data);
            setIsLoading(false);
        } catch (error) {
            console.error('게시물을 불러오는데 실패했습니다', error.response?.data || error.message);
            setPosts([]);
            setIsLoading(false);
        }
    };

    const handleFollowClick = async (following_id) => {
        try {
            const user_id = user.id; // 현재 사용자의 ID 사용
            const response = await axios.post(`${API_BASE_URL}/api/main/follow/request/`, {
                following_id: following_id,
                follower_id: user_id
            });
            setFollowing(true);
        } catch (err) {
            console.error("팔로우 요청 실패", err);
        }
    };

    const checkFollow = async (mans_id) => {
        console.log('checkFollow', mans_id);
        try {
            const response = await axios.get(`${API_BASE_URL}/api/main/following/check/`, {
                params: {
                    user_id: mans_id, // 팔로우 하려는 상대
                    follower_id: user.id // 현재 사용자
                }
            });
            setFollowing(response.data.isFollowing);
        } catch (err) {
            console.error(`팔로우 상태 확인 실패`, err);
        }
    };

    const handleUnfollowClick = async (following_id) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/api/main/unfollow/request/`, {
                following_id: following_id,
                follower_id: user.id
            });
            setFollowing(false);
        } catch (err) {
            console.error('언팔로우 요청 실패', err);
        }
    };

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
        if (profile.id) {
            checkFollow(profile.id);
        }
    }, [profile]);
    console.log('profile', profile);
    return (
        <div className='my-space-container'>
            <div className='my-space-container__profile'>
                <div className='my-space-container__profile-main'>
                    <img src={profile.is_animal ? profile.profile?.profile_pic_url : profile.profile?.profile_pic || defaultImg} 
                    alt="프로필 이미지" 
                    className='my-space-container__profile-img'
                    />
                    <div className='my-space-container__profile-main-info'>
                        <div className='nickname-and-btn'>
                            {profile && <p className='nickname'>{profile.profile?.nickname || profile.nickname}</p>}
                            {isOwnProfile ? (
                                <Link to="/profile/edit" className="edit-profile-btn">수정</Link>
                            ) : (
                                <button 
                                    className='follow-btn'
                                    onClick={() => isFollowing ? handleUnfollowClick(username) : handleFollowClick(username)}
                                >
                                    {isFollowing ? '언팔로우' : '팔로우'}
                                </button>
                            )}
                        </div>
                        
                        <p className='username'>@{username}</p>
                        <p className='bio'>{profile.is_animal? '' : profile.profile?.bio || profile.bio}</p>
                        <Link to={`/animal-dm/${username}`}>메세지</Link>
                    </div>
                </div>
                <div className='my-space-container__profile-follow'>
                    <Link to={`/profile/followlist/${username}/follower`} state={{ nickname: profile.profile?.nickname }}>
                        <p className='follower'>팔로워 <span>{profile.followers_count}</span></p>
                    </Link>
                    <Link to={`/profile/followlist/${username}/following`} state={{ nickname: profile.profile?.nickname }}>
                        <p className='following'>팔로잉 <span>{profile.following_count}</span></p>
                    </Link>
                </div>
            </div>
            <div className='ctrl-box'>
                <button
                    className={`mypost-btn ${activeTab === 'mypost' ? 'active' : ''}`}
                    onClick={() => setActiveTab('mypost')}
                    role="tab"
                    aria-selected={activeTab === 'mypost'}
                >
                    게시물
                </button>
                {profile.is_animal ? 
                    <button
                        className={`like-btn ${activeTab === 'animal-detail' ? 'active' : ''}`}
                        onClick={() => setActiveTab('animal-detail')}
                        role="tab"
                        aria-selected={activeTab === 'animal-detail'}
                    >
                        상세정보
                    </button>
                    :
                    <button
                        className={`like-btn ${activeTab === 'like' ? 'active' : ''}`}
                        onClick={() => setActiveTab('like')}
                        role="tab"
                        aria-selected={activeTab === 'like'}
                    >
                        좋아요
                    </button>
                }
            </div>
            {activeTab !== 'animal-detail' &&
                <div className='my-space-container__posts'>
                    {isLoading ? (
                        <p>로딩 중...</p>
                    ) : posts && posts.length > 0 ? (
                        <ul className="main-container__post-list">
                            {posts.map((post) => (
                                <PostForm key={post.id} post={post} formatDate={formatDate} />
                            ))}
                        </ul>
                    ) : (
                        <p>{activeTab === 'like' ? '좋아요한 게시물이 없습니다' : '등록된 게시물이 없습니다'}</p>
                    )}
                </div>
            }
            {activeTab === 'animal-detail' && 
                <div className='my-space-container__posts'>
                    <p>품종: {profile?.profile.breed}</p>
                    <p>나이: {profile?.profile.age}</p>
                    <p>성별: {profile?.profile.sex}</p>
                </div>
            }
        </div>
    );
}

export default ProfileDetailForm;