import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../snippets';
import './friend.css';
import deleteIcon from '../static/img/delete.png';
import chatIcon from '../static/img/chat.png';
import { URLManagement, getCookie } from '../snippets';

function FriendListForm() {
    const [friends, setFriends] = useState([]);
    const [ws, setWs] = useState(null);
    const { user } = useContext(UserContext);
    const { setFriendUsername} = useContext(UserContext);
    const { setFriendID } = useContext(UserContext);
    const API_BASE_URL = URLManagement('http');
    const WS_BASE_URL = URLManagement('ws');

    const navigate = useNavigate();

    const initiateDM = (friendUsername, friendID) => {
        setFriendUsername(friendUsername);
        setFriendID(friendID);
        navigate(`/dm/${friendID}`);
    };

    const deleteFriend = async (friendUsername, friendNickname) => {
        // 사용자에게 삭제 확인 요청
        const isConfirmed = window.confirm(`정말로 "${friendNickname}"을(를) 친구 목록에서 삭제하시겠습니까? 삭제후엔 되돌릴 수 없습니다.`);
        if (isConfirmed) {
            try {
                const csrfToken = getCookie('csrftoken');
                // 친구삭제요청
                await axios.delete(`${API_BASE_URL}/api/friend/remove/${friendUsername}/`, {
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    withCredentials: true
                });
                // 메세지삭제요청
                await axios.delete(`${API_BASE_URL}/api/chat/remove-messages/${friendUsername}/`, {
                    headers: {'X-CSRFToken': csrfToken},
                    withCredentials: true
                });
                // 양쪽 알림삭제
                await axios.delete(`${API_BASE_URL}/api/notification/delete-both/dm/${friendUsername}/`, {
                    headers: {'X-CSRFToken': csrfToken},
                    withCredentials: true
                });
                // 성공적으로 삭제되면 친구 목록에서 해당 친구 제거
                setFriends(friends.filter(friend => friend.username !== friendUsername));
            } catch (error) {
                console.error("친구 삭제에 실패했습니다.", error);
            }
        }
    };

    const deleteNotification = async (friendUsername) => {
        try {
            const csrfToken = getCookie('csrftoken');
            await axios.post(`${API_BASE_URL}/api/notification/delete/dm/${friendUsername}/`, {}, { // 두 번째 인자로 빈 객체를 전달
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
        } catch (error) {
            console.error("알림 삭제에 실패했습니다.", error);
        }
    };

    const fetchFriends = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/friend/list`, {
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
        fetchFriends(); // 최초 로드 시 친구 목록 가져오기
        //const intervalId = setInterval(fetchFriends, 1000); // 1초마다 친구 목록 갱신
        //return () => clearInterval(intervalId); 
    }, [user, navigate]);

    useEffect(() => {
        const newWs = new WebSocket(`${WS_BASE_URL}/ws/chat/dm/?type=friend_list&friend_username=none`);
        newWs.onopen = () => {
            const friendUsernameList = friends.map(friend => friend.username);
            newWs.send(JSON.stringify({ type: 'friend_list', username_list: friendUsernameList}));
        };

        newWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // 새로운 DM이 있을 때만 친구 목록을 갱신
            if (data.type === 'dm_message') {
                fetchFriends();
            }
        };
        return () => {
            newWs.close();
        };
    }, [user, friends]);

    return (
        <div className="friendListForm-container">
            <p className='back-btn'><BackButton /></p>
            {friends.length > 0 ? (
                <ul className="friendList">
                    {friends.map((friend, index) => (
                        <li key={index} className="friendItem">
                            <img src={`${API_BASE_URL}${friend.profile_pic}`} alt="Profile" className="friendProfilePic" />
                            <div className="friendInfo">
                                <span className="friendNickname">{friend.nickname}
                                    {friend.unread_count > 0 && <span className="unreadDot">{friend.unread_count}</span>}
                                </span>
                                <span className="friendSchool">{friend.school}</span>
                                <span className="friendBio">{friend.bio}</span>
                                {friend.recent_message && (
                                    <div className='last-message'>
                                    {friend.recent_message.length > 15 ? `${friend.recent_message.substring(0, 15)}...` : friend.recent_message}
                                    </div>
                                )}
                            </div>
                            <div className='friendManage'>
                                <img src={chatIcon} className='icon chatIcon' onClick={()=>{initiateDM(friend.username, friend.id); deleteNotification(friend.username);}} alt="DM"></img>
                                <img src={deleteIcon} className='icon deleteIcon' onClick={() => deleteFriend(friend.username, friend.nickname)} alt="Delete"></img>
                            </div>
                            <div className='friendManage-fold'>
                                <img src={chatIcon} className='icon chatIcon' onClick={()=>{initiateDM(friend.username, friend.id); deleteNotification(friend.username);}} alt="DM"></img>
                                <img src={deleteIcon} className='icon deleteIcon' onClick={() => deleteFriend(friend.username, friend.nickname)} alt="Delete"></img>
                            </div>
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
