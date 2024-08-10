import React, { createContext, useState, useEffect } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [friendUsername, setFriendUsername] = useState('');
    const [friendID, setFriendID] = useState('');

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                const parsedUser = JSON.parse(storedUser);
                setUser(parsedUser);
            } catch (error) {
                console.error('Failed to parse stored user data:', error);
                localStorage.removeItem('user');
            }
        }
    }, []);

    const updateUser = (userData) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    };

    const clearUser = () => {
        setUser(null);
        localStorage.removeItem('user');
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