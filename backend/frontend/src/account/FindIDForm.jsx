// FindIDForm.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { URLManagement } from '../snippets';

function FindIDForm() {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const API_BASE_URL = URLManagement('http');
    const [tempMessage, setTempMessage] = useState('');

    const handleChange = (e) => {
        setEmail(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setTempMessage('메일을 전송중입니다. 잠시만 기다려주세요.');

        try {
            const response = await axios.post(`${API_BASE_URL}/api/recover-username/`, { email });
            setMessage(response.data.message);
        } catch (error) {
            setMessage('서버로부터 응답을 받지 못했습니다.');
        }
    };
    const showTempMessage = (msg) => {
        setTempMessage(msg); // 메시지 설정
        setTimeout(() => {
            setTempMessage(''); // 2초 후 메시지 제거
        }, 1500);
    };
    useEffect(() => {
        if (message) {
            showTempMessage(message);
        }
    }, [message]);

    return (
        <div className='findaccount-container'>
            <div className='link-box'>
                <Link to="/find-id" className='forgot-link active-link'>
                    <p>아이디 찾기</p>
                </Link>
                <Link to="/find-pw" className='forgot-link'>
                    <p>비밀번호 찾기</p>
                </Link>
            </div>
            {tempMessage && <div className='error'>{tempMessage}</div>}
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="이메일 주소"
                    value={email}
                    onChange={handleChange}
                    required
                />
                <button type="submit">아이디 찾기</button>
            </form>
            <div className='notice'>
                <p>※ 아이디를 잊으셨나요? 이메일을 입력하시면 가입된 아이디를 확인할 수 있습니다.</p>
                <p>※ 만약 이메일이 오지 않는다면, 스펨메일함을 확인해주세요.</p>
            </div>
        </div>
    );
};

export default FindIDForm;
