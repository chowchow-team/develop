import React, { useState } from 'react';
import axios from 'axios';
import FollowRecommendation from './FollowRecommendation'; 

const FollowRequestForm = () => {
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');

    const handleFollow = async (following_id) => {
        try {
            const user_id = 7; // 현재 사용자의 사용자 이름으로 대체
            const response = await axios.post('http://localhost:8000/api/main/follow/request/', {
                following_id: following_id,
                follower_id: user_id
            });
            setStatus(response.data.status);
        } catch (err) {
            if (err.response) {
                setError(err.response.data.error);
            }
        }
    };

    const handleUnfollow = async (following_id) => {
        try {
            const user_id = 7;
            const response = await axios.post('http://localhost:8000/api/main/unfollow/request/',{
                following_id : following_id,
                follower_id : user_id
            });
            setStatus(response.data.status);
        } catch (err) {
            if (err.response) {
                setError(err.response.data.error)
            }
        }
    };
    return (
        <div>
            <FollowRecommendation onFollow={handleFollow} onUnfollow={handleUnfollow}/>
            {status && <p>Success: {status}</p>}
            {error && <p>Error: {error}</p>}
        </div>
    );
};

export default FollowRequestForm;

