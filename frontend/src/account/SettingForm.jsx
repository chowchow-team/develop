import React, { useContext, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { UserContext } from '../UserContext';
import { URLManagement, getCookie } from '../snippets';

function SettingForm() {
    const { setUser } = useContext(UserContext);
    const { user } = useContext(UserContext);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');

    const handleDeleteAccount = async () => {
        const isConfirmed = window.confirm("정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.");

        if (isConfirmed) {
            const csrfToken = getCookie('csrftoken');
            try {
                await axios.post(`${API_BASE_URL}/api/delete-account/`, {}, {
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    withCredentials: true
                });
                alert("계정이 성공적으로 삭제되었습니다.");
                // 사용자 상태 업데이트 및 로그인 페이지로 리디렉션
                setUser(null);
                localStorage.removeItem('user'); // 로컬 스토리지에서 사용자 정보 제거
                navigate('/login');
            } catch (error) {
                alert("계정을 삭제하는 중 오류가 발생했습니다.");
            }
        }
    };
    useEffect(() => {
        // 로그인되지 않은 경우 로그인 페이지로 리디렉트
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    return (
        <div className="setting-container">
            <div className="setting-box">
                <Link to="/password-change" className="changePassword">
                    <div className="setPassword">
                        <p>비밀번호 변경</p>
                        <p>비밀번호를 변경합니다</p>
                    </div>
                </Link>
                <div className="delUser" onClick={handleDeleteAccount}>
                    <p>회원탈퇴</p>
                    <p>모든 계정 정보를 삭제합니다</p>
                </div>
            </div>
        </div>
    )
}

export default SettingForm;