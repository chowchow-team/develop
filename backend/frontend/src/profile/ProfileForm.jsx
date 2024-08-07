import React, { useState, useEffect, useContext } from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import defaultImg from '../static/img/logo.png';
import {URLManagement, getCookie} from '../snippets';

import './profile.css';

function ProfileForm() {
    const [profile, setProfile] = useState({
        nickname: '',
        bio: '',
        profilePic: '',
        profilePicPreview: ''
    });
    const [error, setError] = useState('');
    const [tempMessage, setTempMessage] = useState('');

    const { user } = useContext(UserContext);
    const navigate = useNavigate();
    const API_BASE_URL = URLManagement('http');

    useEffect(() => {
        if (!user){
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
            setProfile(response.data);
        } catch (error) {
            setError(error.response.data.message);
            console.error('프로필 정보를 불러오는데 실패했습니다', error);
        }
    };
    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setProfile({ ...profile, profilePic: e.target.files[0] });

            // 파일 미리보기를 위한 FileReader 사용
            const reader = new FileReader();
            reader.onload = () => {
                setProfile(prevProfile => ({ ...prevProfile, profilePicPreview: reader.result }));
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setProfile({
            ...profile,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const formData = new FormData();
            const csrfToken=getCookie('csrftoken');
            formData.append('nickname', profile.nickname);
            formData.append('bio', profile.bio);
            formData.append('username', user.username);
            // 파일이 있는 경우에만 추가
            if (profile.profilePic) {
                formData.append('profile_pic', profile.profilePic);
            }
            await axios.post(`${API_BASE_URL}/api/profile/${user.username}/update/`, formData, {
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
            const successMessage = '프로필이 업데이트되었습니다.';
            setError(successMessage);
            setTempMessage(successMessage);
            setTimeout(() => setTempMessage(''), 5000);

        } catch (error) {
            let firstErrorMessage = "";
            const firstKey = Object.keys(error.response.data)[0];
            if (firstKey && error.response.data[firstKey].length > 0) {
                firstErrorMessage = error.response.data[firstKey][0];
            }

            setError(firstErrorMessage); // 오류 메시지 상태 설정
            // showTempMessage 함수 호출 대신 직접 tempMessage 상태를 설정하여 오류 메시지 표시
            setTempMessage(firstErrorMessage);
            setTimeout(() => setTempMessage(''), 5000);
        }
    };

    const showTempMessage = (error) => {
        setTempMessage(error); // 메시지 설정
        setTimeout(() => {
            setTempMessage(''); // 2초 후 메시지 제거
        }, 2000);
    };

    useEffect(() => {
        if (error) {
            showTempMessage(error);
        }
    }, [error]);

    return (
        <div className='profile-page-container'>
            <BackButton />
            {tempMessage && <div className='error'>{tempMessage}</div>}
            <form onSubmit={handleSubmit}>
                <div className='profile-header'>
                    <img src={profile.profilePicPreview||`${API_BASE_URL}${profile.profile_pic}`} alt="프로필 사진" />
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
