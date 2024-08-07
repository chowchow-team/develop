// FindPWForm.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { URLManagement } from '../snippets';

function FindPWForm() {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const API_BASE_URL = URLManagement('http');
    const [tempMessage, setTempMessage] = useState('');

    const handleEmailChange = (e) => {
        setEmail(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setTempMessage('등록된 정보를 검토중입니다. 잠시만 기다려주세요.');

        try {
            const response = await axios.post(`${API_BASE_URL}/api/pwreset-request/`, { email });
            setMessage('임시 비밀번호가 이메일로 전송되었습니다. 이메일을 확인해주세요.');
        } catch (error) {
            setMessage(error.response.data.error);
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
                <Link to="/find-id" className='forgot-link'>
                    <p>아이디 찾기</p>
                </Link>
                <Link to="/find-pw" className='forgot-link active-link'>
                    <p>비밀번호 찾기</p>
                </Link>
            </div>
            {tempMessage && <div className='error'>{tempMessage}</div>}
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="이메일 주소"
                    value={email}
                    onChange={handleEmailChange}
                    required
                />
                <button type="submit">비밀번호 찾기</button>
            </form>
            <div className='notice'>
                <p>※ 비밀번호를 잊으셨나요? 이메일을 입력하시면 비밀번호 재설정 링크를 보내드립니다.</p>
                <p>※ 만약 이메일이 오지 않는다면, 스펨메일함을 확인해주세요.</p>
            </div>
        </div>
    );
};

export default FindPWForm;
