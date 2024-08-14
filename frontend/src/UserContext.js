import React, { createContext, useState, useEffect } from 'react';

export const UserContext = createContext();

/* 드리는 말씀:
로그인 유지 구현을 위해 구현된 부분으로 실질적인 로그인상태는 세션으로 관리됩니다.
로컬스토리지는 조작될 수 있지만, 서버에 인증차단이 구현되어 있으므로 이것이 보안취약점으로 연결되지 않습니다.
유저편의성을 위해 구현된 부분입니다. 서버의 세션만료시간인 2주에 맞추어 로컬스토리지 저장기간 2주를 구현하였습니다.
*/

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [friendUsername, setFriendUsername] = useState('');
    const [friendID, setFriendID] = useState('');

    const EXPIRY_TIME = 14 * 24 * 60 * 60 * 1000;

    useEffect(() => {
        const storedData = localStorage.getItem('userData');
        if (storedData) {
            try {
                const { user: storedUser, expiry } = JSON.parse(storedData);
                if (new Date().getTime() < expiry) {
                    setUser(storedUser);
                } else {
                    localStorage.removeItem('userData');
                }
            } catch (error) {
                alert('로그인 정보를 불러오는 중 오류가 발생했습니다.');
                localStorage.removeItem('userData');
            }
        }
    }, []);

    const updateUser = (userData) => {
        setUser(userData);
        const expiryTime = new Date().getTime() + EXPIRY_TIME;
        localStorage.setItem('userData', JSON.stringify({
            user: userData,
            expiry: expiryTime
        }));
    };

    const clearUser = () => {
        setUser(null);
        localStorage.removeItem('userData');
    };

    const getUserId = () => {
        return user ? user.id : null;
    };

    return (
        <UserContext.Provider value={{ 
            user, 
            updateUser,
            clearUser,
            getUserId,
            friendUsername, setFriendUsername,
            friendID, setFriendID
        }}>
            {children}
        </UserContext.Provider>
    );
};