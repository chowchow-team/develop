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
            if (error.response && error.response.data) {
                const errorData = error.response.data;
                if (typeof errorData === 'string') {
                    errorMessage = errorData;
                } else if (typeof errorData === 'object') {
                    errorMessage = Object.values(errorData).flat().join(', ');
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