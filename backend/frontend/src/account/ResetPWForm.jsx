import React, { useState } from 'react';
import axios from 'axios';
import './account.css';
import { URLManagement, getCookie } from '../snippets';

function ChangePWForm() {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleCurrentPasswordChange = (e) => setCurrentPassword(e.target.value);
    const handleNewPasswordChange = (e) => setNewPassword(e.target.value);
    const handleConfirmNewPasswordChange = (e) => setConfirmNewPassword(e.target.value);

    const API_BASE_URL = URLManagement('http');

    const changePassword = async () => {
        if (newPassword !== confirmNewPassword) {
            setMessage('새 비밀번호가 일치하지 않습니다.');
            return;
        }
        const csrfToken=getCookie('csrftoken');
        try {
            // 비밀번호 변경 처리 API로 요청을 보냅니다.
            const response = await axios.post(`${API_BASE_URL}/api/pw-change/`, {
                old_password: currentPassword,
                new_password: newPassword,
            }, {
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
            setMessage('비밀번호가 성공적으로 변경되었습니다.');
        } catch (error) {
            setMessage('비밀번호 변경 요청 처리 중 오류가 발생했습니다.');
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        changePassword();
    };

    return (
        <div className='pwreset-container'>
            <form onSubmit={handleSubmit}>
                <div className='currentpw'>
                    <label htmlFor="currentPassword">현재 비밀번호</label>
                    <p>현재 비밀번호를 입력하세요</p>
                    <input
                        type="password"
                        id="currentPassword"
                        value={currentPassword}
                        onChange={handleCurrentPasswordChange}
                        required
                    />
                </div>
                <div className='newpw'>
                    <label htmlFor="newPassword">새 비밀번호</label>
                    <p>새로운 비밀번호를 입력하세요</p>
                    <input
                        type="password"
                        id="newPassword"
                        value={newPassword}
                        onChange={handleNewPasswordChange}
                        required
                    />
                </div>
                <div className='pwconfirm'>
                    <label htmlFor="confirmNewPassword">비밀번호 확인</label>
                    <p>새로운 비밀번호를 다시 입력하세요</p>
                    <input
                        type="password"
                        id="confirmNewPassword"
                        value={confirmNewPassword}
                        onChange={handleConfirmNewPasswordChange}
                        required
                    />
                </div>
                <button type="submit" className='pwreset-btn'>비밀번호 변경</button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
};

export default ChangePWForm;
