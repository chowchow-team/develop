import React, { useEffect, useState } from 'react';
import axios from 'axios';

const FollowRecommendation = ({onFollow, onUnfollow}) => {
    const [recommendations, setRecommendations] = useState([]);


    useEffect(() =>{
        const fetchRecommendations = async() => {
            try{
                const response = await axios.get('http://localhost:8000/api/main/follow/');
                const recommendationsWithFollowState = await Promise.all(response.data.map(async user => {
                    const followCheckResponse = await axios.get('http://localhost:8000/api/main/following/check',{params:{
                        user_id:user.id,
                        follower_id:7 // 사용자의 id로 수정해야함
                    }});
                    return {
                        ...user,
                        isFollowing: followCheckResponse.data.isFollowing
                    };
                }));
                setRecommendations(recommendationsWithFollowState);
            }catch(error){
                console.error('Failed to fetch recommendations:',error);
            }
        };
        fetchRecommendations();
    }, []);

    const handleFollowClick = async (user) => {
        if (user.isFollowing){
            await onUnfollow(user.id)
        } else {
            await onFollow(user.id);
        }
    
        setRecommendations(recommendations.map(recommendation =>
            recommendation.id === user.id ? { ...recommendation, isFollowing: !recommendation.isFollowing} : recommendation
        ));
    }

    return (
        <div>
            <h3>Follow Recommendations</h3>
            <ul>
                {recommendations.map(user => (
                    <li key={user.id}>
                        {user.username}
                        <button onClick={() => handleFollowClick(user)}>
                            {user.isFollowing ? 'Unfollow' : 'Follow'}    
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default FollowRecommendation;
