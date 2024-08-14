import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import { URLManagement, getCookie } from '../snippets';
import './profile.css';

function ProfileForm() {
    const [profile, setProfile] = useState({
        nickname: '',
        bio: '',
        profilePic: null,
        profilePicPreview: ''
    });
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const { user } = useContext(UserContext);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');

    useEffect(() => {
        if (!user) {
            navigate('/login');
        } else if (user.username) {
            fetchProfile();
        }
    }, [user, navigate]);

    const fetchProfile = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/profile/${user.username}/`, {
                withCredentials: true
            });
            const profileData = response.data.profile || {};
            setProfile(prevProfile => ({
                ...prevProfile,
                nickname: profileData.nickname || '',
                bio: profileData.bio || '',
                profilePicPreview: profileData.profile_pic ? `${API_BASE_URL}${profileData.profile_pic}` : ''
            }));
        } catch (error) {
            setError('프로필 정보를 불러오는데 실패했습니다');
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            const file = e.target.files[0];
            setProfile(prevProfile => ({ ...prevProfile, profilePic: file }));

            const reader = new FileReader();
            reader.onload = (e) => {
                setProfile(prevProfile => ({ ...prevProfile, profilePicPreview: e.target.result }));
            };
            reader.readAsDataURL(file);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setProfile(prevProfile => ({
            ...prevProfile,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const formData = new FormData();
            formData.append('nickname', profile.nickname);
            formData.append('bio', profile.bio);
            if (profile.profilePic) {
                formData.append('profile_pic', profile.profilePic);
            }

            const csrfToken = getCookie('csrftoken');
            await axios.post(`${API_BASE_URL}/api/profile/${user.username}/update/`, formData, {
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'multipart/form-data'
                },
                withCredentials: true
            });

            setMessage('프로필이 업데이트되었습니다.');
            setTimeout(() => setMessage(''), 5000);
        } catch (error) {
            let errorMessage = '프로필 업데이트에 실패했습니다.';
            if (!error.response) {
                errorMessage = '네트워크 오류가 발생했습니다. 인터넷 연결을 확인해주세요.';
            } else {
                const { status, data } = error.response;
        
                switch (status) {
                    case 400:
                        errorMessage = '프로필 업데이트에 실패했습니다.';
                        break;
                    case 401:
                        errorMessage = '인증에 실패했습니다. 다시 로그인해주세요.';
                        break;
                    case 403:
                        errorMessage = '너무 많은 요청을 보냈습니다. 잠시 후 다시 시도해주세요.';
                        break;
                    case 404:
                        errorMessage = '요청한 리소스를 찾을 수 없습니다.';
                        break;
                    case 500:
                        errorMessage = 'jpg, jpeg, png 형식의 이미지만 업로드할 수 있습니다.';
                        break;
                    default:
                        errorMessage = '오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
                }
            }
            setError(errorMessage);
            setTimeout(() => setError(''), 5000);
        }
    };

    return (
        <div className='profile-page-container'>
            <BackButton />
            {message && <div className='error'>{message}</div>}
            {error && <div className='error'>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className='profile-header'>
                    <img src={profile.profilePicPreview || `${API_BASE_URL}${profile?.profile_pic}`} alt="프로필 사진" />
                    <input
                        type="text"
                        name="nickname"
                        value={profile.nickname}
                        onChange={handleInputChange}
                        placeholder="닉네임"
                    />
                    <div className="file-upload-wrapper" onClick={() => document.getElementById('file-upload').click()}>
                        <input
                            id="file-upload"
                            type="file"
                            name="profilePic"
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                        />
                        <div className="file-upload-content">
                            여기에 프로필 이미지 추가하기
                        </div>
                    </div>
                </div>
                <div className='profile-bio'>
                    <textarea
                        name="bio"
                        value={profile.bio}
                        onChange={handleInputChange}
                        placeholder="자기소개"
                    />
                </div>
                <button type="submit" className='profile-submit'>프로필 업데이트</button>
            </form>
        </div>
    );
}

export default ProfileForm;