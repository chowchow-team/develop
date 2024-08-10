import React, { useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { UserContext } from '../UserContext';
import { URLManagement, getCookie, removeCookie } from '../snippets';
import { SEOMetaTag } from '../snippets';
import logo from '../static/img/logo.png';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { user, updateUser } = useContext(UserContext);
    const [tempMessage, setTempMessage] = useState('');
    const API_BASE_URL = URLManagement('http');

    useEffect(() => {
        if (user) {
            navigate('/');
        }
    }, [user, navigate]);

    useEffect(() => {
        removeCookie('sessionid');
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const csrfToken = getCookie('csrftoken');
        try {
            const response = await axios.post(`${API_BASE_URL}/api/login/`, {
                username,
                password
            }, {
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
            updateUser({ username: username, ...response.data.user });
            navigate('/');
        } catch (error) {
            setError(error.response?.data?.error || '로그인 실패. 다시 시도해주세요.');
        }
    };

    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(''), 1500);
            return () => clearTimeout(timer);
        }
    }, [error]);

    return (
        <div className='login-container'>
            <SEOMetaTag 
                title='챠우챠우: 로그인'
                description='대학생 커뮤니티 몽글몽글에서 다른 학교의 친구들을 만나보세요'
                keywords='챠우챠우, 유기견, 유기동물, sns, 동물sns'
            />
            <div className='logo-img'>
                <img src={logo} alt="챠우챠우 로고" />
                <div className='logo-span'>                
                    <span className='logo-l'>챠우챠우</span>
                </div>
            </div>
            {error && <div className='error'>{error}</div>}
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    name="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="아이디"
                    required
                />
                <input
                    type="password"
                    name="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="비밀번호"
                    required
                />
                <button type="submit">로그인</button>
            </form>
            <Link to="/signup" className='signup-link'>
                <p>챠우챠우에 처음이신가요? <span style={{color:"#F07489", marginLeft:"1rem"}}>회원가입</span></p>
            </Link>
            <Link to="/find-id" className='signup-link'>
                <p style={{color:"#737373"}}>아이디/비밀번호 찾기</p>
            </Link>
        </div>
    );
}

export default LoginForm;