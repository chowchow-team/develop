import React, { useState, useContext, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import './dm.css';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import { URLManagement, getCookie } from '../snippets';

function AnimalDMForm() {
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isKeyboardActive, setIsKeyboardActive] = useState(false);
    const [profile, setProfile] = useState(null);
    const { user } = useContext(UserContext);
    const location = useLocation();

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);
    const navigate = useNavigate();

    let { username } = useParams();

    const API_BASE_URL = URLManagement('http');

    function setScreenSize2() {
        let vh = (window.outerHeight-15) * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    function setScreenSize() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    const fetchProfile = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/profile/${username}/`, {
                withCredentials: true
            });
            setProfile(response.data);
        } catch (error) {
            //alert('프로필 정보를 불러오는데 실패했습니다');
        }
    };

    useEffect(() => {
        const fetchChat = async () => {
            if (profile && profile.profile && profile.profile.id) { // profile과 profile.profile이 null이 아닌지 체크
                try {
                    const response = await axios.get(`${API_BASE_URL}/api/llm/chat/`, {
                        withCredentials: true,
                        params: {
                            "other_user_id": profile.profile.id,
                        }
                    });
                    setChat(response.data);
                } catch (error) {
                    //alert('채팅 내용을 불러오는데 실패했습니다');
                }
            }
        };
    
        fetchChat(); // profile 객체가 존재하는지에 관계 없이 처음에는 fetchChat()을 실행
    
    }, [profile]); // profile 객체가 변경될 때마다 useEffect 재실행
    
    

    useEffect(() => {
        setScreenSize();
        window.addEventListener('resize', setScreenSize);
        return () => {
            window.removeEventListener('resize', setScreenSize);
        };
    }, [setIsKeyboardActive]);


    useEffect(() => {
        const timer = setTimeout(() => {
            if(isKeyboardActive === false){
                setScreenSize();
                window.scrollTo(0, 0);
            }
        }, 200);
        return () => clearTimeout(timer);
    }, [isKeyboardActive]);

    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    useEffect(() => {
        fetchProfile();
        // 채팅 내용 불러오기
        axios.get(`${API_BASE_URL}/api/chat/dm/${username}`, {
            withCredentials: true
        })
        .then(response => {
            setChat(response.data.reverse());
        })
        .catch(error => {
            //alert('채팅 내용을 불러오는데 실패했습니다');
        });
    }, [username]);

    useEffect(() => {
        if (messagesEndRef.current) {
            const { scrollHeight, clientHeight, scrollTop } = messagesEndRef.current;
            const isNearBottom = scrollTop >= -300;
            if (isNearBottom) {
                messagesEndRef.current.scrollTop=0;
            }
            if (isKeyboardActive && window.innerWidth<=767) {
                messagesEndRef.current.scrollTop=-10;
            }
        }
    }, [chat, isKeyboardActive]);

    const sendMessage = () => {
        if (message.trim() === '') return;
        setIsLoading(true);
        const csrfToken=getCookie('csrftoken');
        axios.post(`${API_BASE_URL}/api/llm/chat/`, {
            message: message,
            receiver_id: profile.profile?.id
        }, {
            headers: {'X-CSRFToken': csrfToken,},
            withCredentials: true
        })
        .then(response => {
            setChat(prevChat => [
                response.data.bot_message,
                response.data.user_message,
                ...prevChat
            ]);
            setMessage('');
            setIsLoading(false);
        })
        .catch(error => {
            alert('메시지 전송 중 오류가 발생했습니다.');
            setIsLoading(false);
        });
        if (inputRef.current) inputRef.current.value = '';
    };

    const handleKeyDown = (e) => {
        if (e.nativeEvent.isComposing) return;
        if (e.key === 'Enter' && message.trim() !== '') {
            e.preventDefault();
            sendMessage();
        }
    };

    const formatTimestamp = (timestamp) => {
        const date = new Date(timestamp || Date.now());
        const hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? '오후' : '오전';
        const formattedHours = hours % 12 || 12;
        const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
    
        return `${ampm} ${formattedHours}:${formattedMinutes}`;
    }

    return (
        <div className="dm-container">
            <BackButton />
            <div className="dm-messages" ref={messagesEndRef}>
                {isLoading && (
                    <div className="message-bubble their-message">대화 중...</div>
                )}
                {chat.map((msg, index) => (
                    <div key={msg.id} className={`message-container ${msg.sender === user.username ? 'my-message' : 'their-message'}`}>
                        <div className="message-content">
                            <div className="message-bubble">
                                <div className="message-text">{msg.message}</div>
                            </div>
                            <span className="message-timestamp">
                                {formatTimestamp(msg.timestamp)}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input 
                    ref={inputRef}
                    type="text" 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="메시지를 입력하세요"
                    onClick={setScreenSize2}
                    onFocus={() => setIsKeyboardActive(true)}
                    onBlur={() => setIsKeyboardActive(false)}
                    disabled={isLoading}
                />
                <button onClick={sendMessage} disabled={isLoading}>보내기</button>
            </div>
        </div>
    );
}

export default AnimalDMForm;