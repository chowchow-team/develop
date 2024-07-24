import React, { createContext, useState, useEffect } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [friendUsername, setFriendUsername] = useState('');
    const [friendID, setFriendID] = useState('');

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    return (
        <UserContext.Provider value={{ 
            user, setUser,
            friendUsername, setFriendUsername,
            friendID, setFriendID
        }}>
            {children}
        </UserContext.Provider>
    );
};
