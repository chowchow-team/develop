import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../snippets';
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
    const { user, setFriendUsername, setFriendID } = useContext(UserContext);
    const [activeTab, setActiveTab] = useState('follower');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');

    const fetchFriends = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/main/${activeTab}/list/`, {
                params: { user_id: 1 },
                withCredentials: true,
            });
            setFriends(response.data.data || []);
        } catch (error) {
            setError("친구 목록을 불러오는 데 실패했습니다.");
            console.error("친구 목록을 불러오는 데 실패했습니다.", error);
        }
    };

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        fetchFriends();
    }, [user, navigate, activeTab]);

    const handleFollowClick = (friendId) => {
        // 팔로우 버튼 클릭 시 동작을 정의합니다.
        console.log(`Follow button clicked for friend with ID: ${friendId}`);
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
                    팔로워
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
                        <li key={index} className="friendItem">
                            <img src={`${API_BASE_URL}${friend.profile_pic}`} alt="Profile" className="friendProfilePic" />
                            <div className="friendInfo">
                                <span className="friendNickname">{friend.nickname}</span>
                                <span className="friendUsername">@{friend.username}</span>
                                <div>
                                    {friend.bio && <TruncatedBio bio={friend.bio} />}
                                </div>
                                
                            </div>
                            <button
                                className='follow-btn'
                                onClick={() => handleFollowClick(friend.id)}
                            >
                                팔로우
                            </button>
                        </li>
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
