import React, { useState, useContext, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './chat.css';
import accept from '../static/img/accept.png';
import reject from '../static/img/reject.png';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import { URLManagement } from '../snippets';
import { OnlineUser } from '../snippets';

function ChatForm() {
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);
    const [ws, setWs] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isMatched, setIsMatched] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isConfirmingEndChat, setIsConfirmingEndChat] = useState(false);
    const [isTyping, setIsTyping] = useState(false); // 상대방의 타이핑 상태를 추적하는 상태 변수
    const [friendRequestReceived, setFriendRequestReceived] = useState(false); // 친구 요청 받았는지 여부
    const [friendRequestSent, setFriendRequestSent] = useState(false); // 친구 요청 보냈는지 여부
    const [friendRequestFrom, setFriendRequestFrom] = useState(''); // 친구 요청을 보낸 사용자
    const [peerUsername, setPeerUsername] = useState('');
    const [tempMessage, setTempMessage] = useState('');
    const [peerInfo, setPeerInfo] = useState('');
    const [isKeyboardActive, setIsKeyboardActive] = useState(false);// 키보드활성상태


    const { user } = useContext(UserContext);
    const messagesEndRef = useRef(null);
    const typingTimeoutRef = useRef(null);
    const inputRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    const WS_BASE_URL = URLManagement('ws');


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

    useEffect(() => {
        // 로그인되지 않은 경우 로그인 페이지로 리디렉트
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    useEffect(() => {
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
    }, [chat, isKeyboardActive]); // chat 상태가 변경될 때마다 실행

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
        return () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                endChat();
                ws.close();
            }
        };
    }, [ws, location]);

    useEffect(() => {
        const handleBeforeUnload = (event) => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                endChat();
            }
        };
    
        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [ws]);
    

    const connectWebsocket = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }

        const newWs = new WebSocket(`${WS_BASE_URL}/ws/chat/random/?type=random&friend_username=none`);
        newWs.onopen = () => {
            setIsConnected(true);
            newWs.send(JSON.stringify({ type: 'start_chat' }));
        };

        newWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'chat':
                    setChat((prevChat) => [{ message: data.message, sender: data.sender },...prevChat]);
                    break;
                case 'match_success':
                    setIsMatched(true);
                    setIsLoading(false);
                    const peerData = data.message.find(info => info.username !== user.username);
                    setPeerInfo(peerData);
                    const start_msg1= `"${peerData.school}"의 누군가와 연결되었습니다!`;
                    const start_msg2= "친구추가를 하면 다음에도 계속 대화할 수 있어요!";
                    setChat((prevChat) => [{ message: start_msg1, sender: user.username },...prevChat]);
                    setChat((prevChat) => [{ message: start_msg2, sender: user.username },...prevChat]);
                    break;
                case 'chat_end':
                    endChat();
                    break;
                case 'typing_start':
                    if (data.sender !== user.username) setIsTyping(true);
                    break;
                case 'typing_end':
                    if (data.sender !== user.username) setIsTyping(false);
                    break;
                case 'friend_request':
                    setFriendRequestReceived(true);
                    setFriendRequestFrom(data.from_username);
                    //메세지함에 도착알림주자
                    const request_msg= "SYSTEM: 친구요청이 도착했습니다. 상단에서 친구요청을 수락/거절해주세요.";
                    setChat((prevChat) => [{ message: request_msg, sender: user.username },...prevChat]);
                    break;
                case 'accept_friend_request':
                    showTempMessage('수락되었습니다.');
                    break;
                case 'reject_friend_request':
                    showTempMessage('거절되었습니다.');
                    break;
                default:
                    break;
            }
        };

        newWs.onclose = () => {
            setIsConnected(false);
            setIsMatched(false);
            endChat();
        };

        setWs(newWs);
    };


    const startChat = () => {
        setChat([]);
        setMessage('');
        setIsLoading(true);
        connectWebsocket();
    };

    const confirmEndChat = () => {
        setIsConfirmingEndChat(true); // 사용자가 처음 "대화 끝"을 클릭했을 때
    };

    const endChat = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'chat_end' }));
            rejectFriendRequest();
            ws.close();
            alert('채팅이 종료되었습니다.'); // WebSocket이 열려있을 때만 alert 호출
        }
        // 연결 상태 초기화
        setWs(null);
        setIsConnected(false);
        setIsMatched(false);
        setChat([]);
        setIsConfirmingEndChat(false);
        setFriendRequestReceived(false);
        setFriendRequestSent(false);
        setIsLoading(false);
    };

    const sendMessage = () => {
        inputRef.current.focus(); // 입력창에 포커스
        if (ws && message) {
            const messageData = { type: 'chat_message', message: message };
            ws.send(JSON.stringify(messageData));
            setMessage('');
            if (inputRef.current) inputRef.current.value = ''; //인풋클릭시 마지막 글자 나오는 오류 해결시도
        }
    };

    const handleTyping = () => {
        if (ws) {
            ws.send(JSON.stringify({ type: 'typing_start', sender: user.username }));
            clearTimeout(typingTimeoutRef.current); // 이전 타이머 취소
            typingTimeoutRef.current = setTimeout(() => { // 새 타이머 설정
                ws.send(JSON.stringify({ type: 'typing_end', sender: user.username }));
            }, 500); // .5초 동안 추가 입력이 없으면 타이핑 종료로 간주
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

    const sendFriendRequest = () => {
        if (ws) {
            const friendRequestData = { type: 'send_friend_request', to_username: user.username }; // 여기서 상대방 사용자명 설정 필요
            ws.send(JSON.stringify(friendRequestData));
            setFriendRequestSent(true);
            const send_request_msg= "SYSTEM: 친구요청을 완료했습니다.";
            setChat((prevChat) => [{ message: send_request_msg, sender: user.username },...prevChat]);
        }
    };

    const acceptFriendRequest = () => {
        if (ws && friendRequestFrom) {
            const acceptionData = { type: 'accept_friend_request', from_username: friendRequestFrom };
            ws.send(JSON.stringify(acceptionData));
            setFriendRequestReceived(false); // 친구 요청 수락 후 상태 초기화
        }
    };

    const rejectFriendRequest = () => {
        if (ws && friendRequestFrom) {
            const rejectionData = { type: 'reject_friend_request', from_username: friendRequestFrom };
            ws.send(JSON.stringify(rejectionData));
            setFriendRequestReceived(false); // 친구 요청 거절 후 상태 초기화
        }
    };

    const showTempMessage = (message) => {
        setTempMessage(message); // 메시지 설정
        setTimeout(() => {
            setTempMessage(''); // 2초 후 메시지 제거
        }, 2500);
    };
    

    return (
        <div className="total-chat-container">
            <div className="chat-container">
                <div className='back-and-onlineuser'>
                    <BackButton />
                    <OnlineUser />
                </div>
                {tempMessage && <div className="temp-message">{tempMessage}</div>}
                <div className="chat-header">
                    {isLoading && <p className='status'>매칭중...</p>}
                    {friendRequestReceived && (
                    <div className='friend-request-box'>
                            <div>
                                <p>친구요청이 도착했습니다!</p>
                                <p>
                                    <button onClick={acceptFriendRequest}>
                                        <img src={accept} alt="수락" />
                                    </button>
                                    <button onClick={rejectFriendRequest}>
                                        <img src={reject} alt="거절" />
                                    </button>
                                </p>
                            </div>
                    </div>
                    )}
                    {isMatched && <p className='friend-btn'><button onClick={sendFriendRequest}>친구 요청</button></p>}
                </div>
                <div className="chat-messages" ref={messagesEndRef}>
                    {/*{isMatched &&
                        <>
                            <p className='first-message'>{`"${peerInfo.school}"의 누군가와 연결되었습니다!`}</p>
                            <p className='first-message'>친구추가를 하면 다음에도 계속 대화할 수 있어요!</p>
                        </>    
                    }*/}
                    {!isMatched &&
                        <>
                            <p className='first-message'>상대방에겐 자신의 학교명만이 노출됩니다.</p>
                            <p className='first-message'>채팅 시작하기"를 눌러 다양한 학교의 친구들을 만나보세요.</p>
                            <p className='first-message'>대화를 끝내거나, 페이지를 벗어날 경우 채팅이 종료됩니다.</p>
                            <p className='first-message'>채팅이 여러번 전송될땐, 로그인을 다시 시도해보세요.</p>
                        </>
                    }
                    {chat.map((msg, index) => (
                        <div
                            key={index}
                            className={`message-bubble ${msg.sender === user.username ? 'my-message' : 'their-message'}`}
                        >
                            {msg.message}
                        </div>
                    ))}
                </div>
                {isTyping && (
                <div className="loading">상대방이 입력중입니다...</div> // "..." 말풍선 표시
                )}
                <div className="chat-input">
                    {isMatched && isConnected && (
                        <>
                            {isConnected &&
                                (isConfirmingEndChat ? (
                                    <button onClick={endChat}>정말?</button> // 사용자가 확인해야 하는 경우
                                ) : (
                                    <button onClick={confirmEndChat}>대화 끝</button> // 초기 상태
                            ))}
                            <input 
                                ref={inputRef}
                                type="text" 
                                value={message} 
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyUp={handleTyping}
                                onKeyDown={handleKeyDown}
                                placeholder="메시지를 입력하세요"
                                onClick={setScreenSize2}
                                onFocus={() => setIsKeyboardActive(true)} // 입력 필드에 포커스가 있을 때
                                onBlur={() => setIsKeyboardActive(false)} // 입력 필드에서 포커스가 사라질 때
                            />
                            <button onClick={sendMessage}>보내기</button>
                        </>
                    )}
                    {!isMatched && (
                        <button onClick={startChat} className="start-chat-button">채팅 시작하기</button>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ChatForm;
