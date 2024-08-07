import { useEffect, useContext, useCallback } from 'react';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { useNavigate } from 'react-router-dom';
import { URLManagement } from '../snippets';
import { getCookie } from '../snippets';

function LogoutForm() {
    const { setUser } = useContext(UserContext);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');

    const handleLogout = useCallback(async () => {
        const csrfToken=getCookie('csrftoken');
        try {
            await axios.post(`${API_BASE_URL}/api/logout/`, {}, {
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
            localStorage.removeItem('user');
            setUser(null);
            navigate('/');
            window.location.reload();
        } catch (error) {
            localStorage.removeItem('user');
            setUser(null);
            navigate('/');
            window.location.reload();
        }
    }, [setUser, navigate]);

    useEffect(() => {
        handleLogout();
    }, [handleLogout]);

    return null;
}

export default LogoutForm;
