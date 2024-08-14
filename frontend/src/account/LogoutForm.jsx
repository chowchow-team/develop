import { useEffect, useContext, useCallback } from 'react';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { useNavigate } from 'react-router-dom';
import { URLManagement, getCookie } from '../snippets';

function LogoutForm() {
    const { clearUser } = useContext(UserContext);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');

    const handleLogout = useCallback(async () => {
        const csrfToken = getCookie('csrftoken');
        try {
            await axios.post(`${API_BASE_URL}/api/logout/`, {}, {
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
        } catch (error) {
            alert('로그아웃 중 오류가 발생했습니다.');
        } finally {
            clearUser();
            navigate('/', { replace: true });
        }
    }, [clearUser, navigate, API_BASE_URL]);

    useEffect(() => {
        handleLogout();
    }, [handleLogout]);

    return null;
}

export default LogoutForm;