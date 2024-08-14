import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { BackButton } from '../snippets';
import {UserContext} from "../UserContext";
import './friend.css';
import { URLManagement, getCookie } from '../snippets';

function TruncatedBio({ bio, maxLength = 100 }) {
    const [isExpanded, setIsExpanded] = useState(false);
    
    if (bio.length <= maxLength) return <span>{bio}</span>;
    
    return (
        <span>
            {isExpanded ? bio : `${bio.substring(0, maxLength)}...`}
            <button className='show-more' onClick={() => setIsExpanded(!isExpanded)}>
                {isExpanded ? '접기' : '더 보기'}
            </button>
        </span>
    );
}

function FriendListForm() {
    const [friends, setFriends] = useState([]);
    const { user, getUserId, setFriendUsername, setFriendID } = useContext(UserContext);
    const [activeTab, setActiveTab] = useState('follower');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');
    const userid = getUserId();

    const fetchFriends = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/main/${activeTab}/list/`, {
                params: { user_id: userid },
                withCredentials: true,
            });
            const fetchedFriends = response.data.data;
    
            if (activeTab === 'following') {
                setFriends(fetchedFriends.map(friend => ({
                    ...friend,
                    isFollowing: true
                })));
            } else {
                const user_id = userid;
                const updatedFriends = [];
    
                for (const friend of fetchedFriends) {  // prevFriends 대신 fetch된 친구 목록을 사용
                    try {
                        const response = await axios.get(`${API_BASE_URL}/api/main/following/check/`, {
                            params:{
                                user_id : friend.id,
                                follower_id: userid
                            }
                        });
                        updatedFriends.push({
                            ...friend,
                            isFollowing: response.data.isFollowing
                        });
                    } catch (err) {
                        setError("팔로우 상태를 업데이트하는 데 실패했습니다.");
                    }
                }
    
                setFriends(updatedFriends);  // 모든 친구의 상태를 업데이트 한 번에 처리
            }
    
        } catch (error) {
            setError("친구 목록을 불러오는 데 실패했습니다.");
        }
    };

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        fetchFriends();
    }, [user, navigate, activeTab]);

    const handleFollowClick = async (e, following_id) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            const user_id = userid; // 현재 사용자의 사용자 id로 대체
            const response = await axios.post(`${API_BASE_URL}/api/main/follow/request/`, {
                    following_id: following_id,
                    follower_id: user_id
                }
            );
            setFriends(prevFriends =>
                prevFriends.map(friend =>
                    friend.id === following_id ? { ...friend, isFollowing: true } : friend
                )
            );
        } catch (err) {
            if (err.response) {
                setError(err.response.data.error);
            }
        }
    };

    const handleUnfollowClick = async (e, following_id) => {
        e.preventDefault();  // 이벤트 전파 중단
        e.stopPropagation();
        try {
            const user_id = userid;
            const response = await axios.post(`${API_BASE_URL}/api/main/unfollow/request/`,{
                following_id : following_id,
                follower_id : user_id
            });
            setFriends(prevFriends =>
                prevFriends.map(friend =>
                    friend.id === following_id ? { ...friend, isFollowing: false } : friend
                )
            );
        } catch (err) {
            if (err.response) {
                setError(err.response.data.error)
            }
        }
    };

    return (
        <div className="friendListForm-container">
            <p className='back-btn'><BackButton /></p>
            <div className='ctrl-box'>
                <button
                    className={`follower-btn ${activeTab === 'follower' ? 'active' : ''}`}
                    onClick={() => setActiveTab('follower')}
                    role="tab"
                    aria-selected={activeTab === 'follower'}
                >
                    팔로우
                </button>
                <button
                    className={`following-btn ${activeTab === 'following' ? 'active' : ''}`}
                    onClick={() => setActiveTab('following')}
                    role="tab"
                    aria-selected={activeTab === 'following'}
                >
                    팔로잉
                </button>
            </div>
            {error && (
                <div className="error-message">
                    <p>{error}</p>
                </div>
            )}
            {friends.length > 0 ? (
                <ul className="friendList">
                    {friends.map((friend, index) => (
                        <Link to={`/profile/${friend.username}`}>
                        <li key={index} className="friendItem">
                            
                            <img src={`${friend.profile_pic}`} alt="Profile" className="friendProfilePic" />
                            <div className="friendInfo">
                                <span className="friendNickname">{friend.nickname}</span>
                                <span className="friendUsername">@{friend.username}</span>
                                <div>
                                    {friend.bio && <TruncatedBio bio={friend.bio} />}
                                </div>
                                
                            </div>
                            <button
                                className='follow-btn'
                                onClick={(e) => friend.isFollowing ? handleUnfollowClick(e, friend.id) : handleFollowClick(e, friend.id)}
                            >
                                {friend.isFollowing ? '언팔로우' : '팔로우'}
                            </button>
                            
                        </li>
                        </Link>
                    ))}
                </ul>
            ) : (
                <div className="no-friends-message">
                    <p>아직 추가된 친구가 없어요</p>
                </div>
            )}
        </div>
    );
}

export default FriendListForm;
