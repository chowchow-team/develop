import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { URLManagement } from '../snippets';

function SignupRedirect({match}) {
    const navigate = useNavigate();
    const { uidb64, token } = useParams();
    const API_BASE_URL = URLManagement('http');

    useEffect(() => {
        const activateEmail = async () => {
          try {
            const response = await axios.get(`${API_BASE_URL}/api/activate/${uidb64}/${token}/`);
            localStorage.removeItem('user');
            // 이메일 인증 성공 시 로그인 페이지로 리디렉션
            navigate('/login');
          } catch (error) {
            alert('이메일 인증에 실패했습니다. 다시 시도해주세요.');
            navigate('/login');
            
          }
        };
        activateEmail();
      }, [navigate, uidb64, token]);
  
    return (
        <div>
          <p>이메일 인증 중입니다...</p>
        </div>
    );
}

export default SignupRedirect;