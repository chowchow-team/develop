import React, { useState, useContext, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import './dm.css';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import { URLManagement } from '../snippets';

function DMForm() {
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);
    const [ws, setWs] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isConfirmingEndChat, setIsConfirmingEndChat] = useState(false);
    const [isTyping, setIsTyping] = useState(false); // 상대방의 타이핑 상태를 추적하는 상태 변수
    const [isKeyboardActive, setIsKeyboardActive] = useState(false);// 키보드활성상태
    const { user } = useContext(UserContext);
    const { friendUsername} = useContext(UserContext);
    const { friendID } = useContext(UserContext);
    const location = useLocation();

    const messagesEndRef = useRef(null);
    const typingTimeoutRef = useRef(null);
    const inputRef = useRef(null);
    const navigate = useNavigate();

    const API_BASE_URL = URLManagement('http');
    const WS_BASE_URL = URLManagement('ws');

    const receivedMessageIds = new Set();

    function setScreenSize2() {
        let vh = (window.outerHeight-15) * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    function setScreenSize() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    useEffect(() => {
        setScreenSize(); // 페이지가 로드될 때 한 번 호출
        // 브라우저 창의 크기가 변경될 때마다 호출
        window.addEventListener('resize', setScreenSize);
        // 컴포넌트가 언마운트될 때 이벤트 리스너 제거
        return () => {
            window.removeEventListener('resize', setScreenSize);
        };
    }, [setIsKeyboardActive]);
    //useEffect(() => {
    //    const interval = setInterval(() => {
    //        if(setIsKeyboardActive === false){
    //            setScreenSize();
    //        }
    //    }, 500);
    //
    //    // 컴포넌트가 언마운트될 때 setInterval을 정리
    //    return () => clearInterval(interval);
    //}, []);

    useEffect(() => { // 화면 재조정시키기 위한거임.
        const timer = setTimeout(() => {
            if(isKeyboardActive === false){
                setScreenSize();
                window.scrollTo(0, 0);
            }
        }, 200);
        return () => clearTimeout(timer);
    }, [isKeyboardActive]);

    useEffect(() => {
        // 로그인되지 않은 경우 로그인 페이지로 리디렉트
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    useEffect(() => {
        connectWebsocket();
        axios.get(`${API_BASE_URL}/api/chat/dm/${friendUsername}`, {
            withCredentials: true
        })
        .then(response => {
            setChat(response.data.reverse());
        })
        .catch(error => {
            console.error('채팅 내용을 불러오는데 실패했습니다.', error);
        })
    },[user]);

    useEffect(() => { // 수정 2월25일: gist에서
        if (messagesEndRef.current) {
            const { scrollHeight, clientHeight, scrollTop } = messagesEndRef.current;
            // 스크롤이 바닥에 거의 도달했는지 확인 (여유분을 두어 완전히 바닥이 아니어도 됨)
            //const isNearBottom = scrollHeight - scrollTop <= clientHeight + 150;
            const isNearBottom = scrollTop >= -300;
            if (isNearBottom) {
                // 스크롤이 거의 바닥에 있을 때만 맨 아래로 스크롤
                //messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
                messagesEndRef.current.scrollTop=0;
            }
            if (isKeyboardActive && window.innerWidth<=767){ //모바일 키보드 올라왔을때
                messagesEndRef.current.scrollTop=-10;
            }
        }
    }, [chat, isKeyboardActive]);

    useEffect(() => {
        return () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                exitDMPage();
                ws.close();
            }
        };
    }, [ws, location]);

    const exitDMPage = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const endDmData = { type: 'end_dm', friend_username: friendUsername };
            ws.send(JSON.stringify(endDmData));
        }
    };

    useEffect(() => {
        // beforeunload 이벤트 리스너를 추가하는 함수
        const handleBeforeUnload = (event) => {
            // 웹소켓이 열려있고, 채팅이 시작된 상태라면 endChat 함수 호출
            if (ws && ws.readyState === WebSocket.OPEN) {
                exitDMPage();
            }
        };
    
        // 이벤트 리스너 등록
        window.addEventListener('beforeunload', handleBeforeUnload);
    
        // 컴포넌트 언마운트 시 이벤트 리스너 제거
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [ws]); 
    
    useEffect(() => { // 이거 지우면 안됨
        return () => {
            exitDMPage();
        };
    }, [ws, friendUsername, location]);

    useEffect(() => { // 화면 재조정시키기 위한거임.
        const timer = setTimeout(() => {
            if(isKeyboardActive === false){
                setScreenSize();
                window.scrollTo(0, 0);
            }
        }, 200);
        return () => clearTimeout(timer);
    }, [isKeyboardActive]);


    const connectWebsocket = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }

        const newWs = new WebSocket(`${WS_BASE_URL}/ws/chat/dm/?type=dm&friend_username=${friendUsername}`);
        newWs.onopen = () => {
            setIsConnected(true);
            newWs.send(JSON.stringify({ type: 'start_dm', friend_username: friendUsername }));
        };

        newWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'dm_message':
                    const [message, dm_id] = data.message;
                    if (!receivedMessageIds.has(dm_id)) {
                        receivedMessageIds.add(dm_id);
                        setChat((prevChat) => [{ id: dm_id, message: message, sender: data.sender }, ...prevChat]);
                    }
                    break;
                default:
                    console.log("[연락주시면 감사하겠습니다.]Unknown message type:", data.type);
            }
        };

        newWs.onclose = () => {
            setIsConnected(false);
        };

        setWs(newWs);
    };

    const sendMessage = () => {
        inputRef.current.focus(); // 입력창에 포커스
        if (ws && message) {
            const messageData = { type: 'dm_message', message: message };
            ws.send(JSON.stringify(messageData));
            setMessage('');
            if (inputRef.current) inputRef.current.value = ''; //인풋클릭시 마지막 글자 나오는 오류 해결시도
        }
    };
    

    const handleKeyDown = (e) => {
        if (e.nativeEvent.isComposing) return;
        if (e.key === 'Enter' && message.trim() !== '') {
            e.preventDefault();
            sendMessage();
            setMessage('');
        }
    };

    const formatTimestamp = (timestamp) => {
        const date = new Date(timestamp || Date.now());
        const hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? '오후' : '오전';
        const formattedHours = hours % 12 || 12; // 0시는 12시로 표시
        const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
    
        return `${ampm} ${formattedHours}:${formattedMinutes}`;
    }

    return (
        <div className="dm-container">
            <BackButton />
            <div className="dm-messages" ref={messagesEndRef}>
                {chat.map((msg, index) => (
                    <div key={index} className={`message-container ${msg.sender === user.username ? 'my-message' : 'their-message'}`}>
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
                {isTyping && (
                    <div className="message-bubble their-message">...</div> // "..." 말풍선 표시
                )}
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
                    onFocus={() => setIsKeyboardActive(true)} // 입력 필드에 포커스가 있을 때
                    onBlur={() => setIsKeyboardActive(false)} // 입력 필드에서 포커스가 사라질 때
                />
                <button onClick={sendMessage}>보내기</button>
            </div>
        </div>
    );
}

export default DMForm;
