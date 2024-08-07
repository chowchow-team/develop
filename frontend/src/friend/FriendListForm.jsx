import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../snippets';
import './friend.css';
import { URLManagement, getCookie } from '../snippets';

function FriendListForm() {
    const [friends, setFriends] = useState([]);
    const { user } = useContext(UserContext);
    const { setFriendUsername} = useContext(UserContext);
    const { setFriendID } = useContext(UserContext);
    const API_BASE_URL = URLManagement('http');

    const [activeTab, setActiveTab] = useState('follower');

    const navigate = useNavigate();

    

    const fetchFriends = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/main/follower/list/`, {
                withCredentials: true
            });
            setFriends(response.data);
        } catch (error) {
            console.error("친구 목록을 불러오는 데 실패했습니다.", error);
        }
    };

    useEffect(() => {
        // 로그인되지 않은 경우 로그인 페이지로 리디렉트
        if (!user) {
            navigate('/login');
            return;
        }
        fetchFriends();
    }, [user, navigate]);
    console.log(friends);


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
            {friends.length > 0 ? (
                <ul className="friendList">
                    {friends.map((friend, index) => (
                        <li key={index} className="friendItem">
                            <img src={`${API_BASE_URL}${friend.profile_pic}`} alt="Profile" className="friendProfilePic" />
                            <div className="friendInfo">
                                <span className="friendNickname">{friend.nickname}</span>
                                <span className="friendUsername">{friend.username}</span>
                                <span className="friendBio">{friend.bio}</span>
                            </div>
                            {/* 팔로우여부 확인필요. 팔로잉탭에선 그냥 다 팔로우로 함됨 */}
                            <button className='follow-btn'>
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
