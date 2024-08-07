import { useState, useEffect } from 'react';
import { URLManagement } from '.';
/*
function OnlineUser() {
    const [onlineUser, setOnlineUser] = useState(0);
    const [ws, setWs] = useState(null);

    const WS_BASE_URL = URLManagement('ws');

    useEffect(() => {
        if (!ws) {
            const websocket = new WebSocket(`${WS_BASE_URL}/ws/count-online/`); // 웹소켓 주소는 필요에 따라 수정
            setWs(websocket);

            websocket.onopen = () => {
                websocket.send(JSON.stringify({ type: 'get_online_users_count' }));
            };

            websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("data: ", data);
                if (data.type === 'online_users_count') {
                    setOnlineUser(data.count);
                    console.log("onlineUser: ", data.count);
                }
            };

            websocket.onclose = () => {
                //console.log('WebSocket disconnected');
            };

            return () => {
                if (websocket && websocket.readyState === WebSocket.OPEN) {
                    websocket.close();
                }
            };
        }
    }, [ws, WS_BASE_URL]);

    //return onlineUser;
    return (
        <p className='online-user'>접속자: {onlineUser}명</p>
    );
}

export default OnlineUser;
*/


function OnlineUser() {
    const [onlineUser, setOnlineUser] = useState(0);
    const [ws, setWs] = useState(null);

    const WS_BASE_URL = URLManagement('ws');

    useEffect(() => {
        const websocket = new WebSocket(`${WS_BASE_URL}/ws/count-online/`); // 웹소켓 주소는 필요에 따라 수정
        setWs(websocket);

        websocket.onopen = () => {
            websocket.send(JSON.stringify({ type: 'get_online_users_count' }));
        };

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("data: ", data);
            if (data.type === 'online_users_count') {
                setOnlineUser(data.count);
                console.log("onlineUser: ", data.count);
            }
        };

        websocket.onclose = () => {
            console.log('WebSocket disconnected');
        };

        return () => {
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.close();
            }
        };
    }, [WS_BASE_URL]);

    return (
        <p className='online-user'>접속자: {onlineUser}명</p>
    );
}

export default OnlineUser;