import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom';
import { BackButton } from '../snippets';
import { UserContext } from "../UserContext";
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

function UserFollowListForm() {
    const [friends, setFriends] = useState([]);
    const { user } = useContext(UserContext);
    
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');
    const { username } = useParams();
    const { flag } = useParams();
    const [activeTab, setActiveTab] = useState(flag); // /profile/followlist/:username/follower or following
    const location = useLocation();
    const nickname = location.state?.nickname;

    const fetchFriends = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/main/${activeTab}/list/`, {
                params: { username: username },
                withCredentials: true,
            });
            const fetchedFriends = response.data.data;
    
            const updatedFriends = [];
    
            for (const friend of fetchedFriends) {
                try {
                    const response = await axios.get(`${API_BASE_URL}/api/main/following/check/`, {
                        params: {
                            user_id: friend.id,
                            follower_id: user.id
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
    
            setFriends(updatedFriends);
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
    }, [user, navigate, activeTab, username]);

    const handleFollowClick = async (following_id) => {
        try {
            await axios.post(`${API_BASE_URL}/api/main/follow/request/`, {
                following_id: following_id,
                follower_id: user.id
            });
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

    const handleUnfollowClick = async (following_id) => {
        try {
            await axios.post(`${API_BASE_URL}/api/main/unfollow/request/`, {
                following_id: following_id,
                follower_id: user.id
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
            <p className='nickname'>{nickname}</p>
            <p className='username'>@{username}</p>
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
                            {user.username !== friend.username && (
                                <button
                                    className='follow-btn'
                                    onClick={() => friend.isFollowing ? handleUnfollowClick(friend.id) : handleFollowClick(friend.id)}
                                >
                                    {friend.isFollowing ? '언팔로우' : '팔로우'}
                                </button>
                            )}
                        </li>
                        </Link>
                    ))}
                </ul>
            ) : (
                <div className="no-friends-message">
                    <p>{activeTab === 'follower' ? '팔로워' : '팔로잉'}이 없습니다.</p>
                </div>
            )}
        </div>
    );
}

export default UserFollowListForm;