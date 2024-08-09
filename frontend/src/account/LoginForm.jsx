import React, { useState, useContext, useEffect } from 'react';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import { UserContext } from '../UserContext';
import { Link } from 'react-router-dom';
import { URLManagement } from '../snippets';
import { getCookie } from '../snippets';
import { removeCookie } from '../snippets';

import { SEOMetaTag } from '../snippets';

import logo from '../static/img/logo.png';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { setUser } = useContext(UserContext);
    const { user } = useContext(UserContext);
    const [tempMessage, setTempMessage] = useState('');
    const API_BASE_URL = URLManagement('http');

    useEffect(() => {
        // 로컬 스토리지에서 사용자 정보를 로드
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, [setUser]);

    useEffect(() => {
        // 이미 로그인 된 경우 메인 페이지로 리디렉션
        if (user) {
            navigate('/');
        }
    }, [user, navigate]);

    useEffect(() => {
        // 로그인 페이지 진입시 쿠키의 sessionid 삭제
        removeCookie('sessionid');
    }   , []);
    

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const csrfToken=getCookie('csrftoken');
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
            localStorage.setItem('user', JSON.stringify({ username: username }));
            setUser({ username: username });
            navigate('/');
        } catch (error) {
            if (error.response && error.response.data) {
                // 서버로부터의 응답에 따라 오류 메시지 설정
                setError(error.response.data.error || '로그인 실패. 다시 시도해주세요.');
            } else {
                setError('서버 오류가 발생했습니다. 다시 시도해주세요.');
            }
        }
    };

    const showTempMessage = (error) => {
        setTempMessage(error); // 메시지 설정
        setTimeout(() => {
            setTempMessage(''); // 2초 후 메시지 제거
        }, 1500);
    };

    useEffect(() => {
        if (error) {
            showTempMessage(error);
        }
    }, [error]);

    return (
        <div className='login-container'>
            <SEOMetaTag 
                title='챠우챠우: 로그인'
                description='대학생 커뮤니티 몽글몽글에서 다른 학교의 친구들을 만나보세요'
                keywords='챠우챠우, 유기견, 유기동물, sns, 동물sns'
                //image='https://미정/og_image.png'
                //url='https://미정/login/'
            />
            <div className='logo-img'>
                <img src={logo} alt="Logo" />
                <div className='logo-span'>                
                    <span className='logo-l'>
                        챠우챠우
                    </span>
                </div>
            </div>
            {tempMessage && <div className='error'>{tempMessage}</div>}
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    name="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="아이디"
                />
                <input
                    type="password"
                    name="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="비밀번호"
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
