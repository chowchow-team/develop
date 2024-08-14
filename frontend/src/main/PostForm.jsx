import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import TruncateText from './TruncateText';
import comment from '../static/img/comment.png';
import view from '../static/img/statistic.png';
import emptyHeart from '../static/img/empty-heart.png';
import filledHeart from '../static/img/filled-heart.png';
import { getCookie } from '../snippets';
import axios from 'axios';

const LikeButton = ({ postId, likeCount, isLiked, onLikeToggle }) => {
  const handleLike = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const csrfToken = getCookie('csrftoken');
    try {
      const response = await axios.post('/api/main/like/', 
        { post_id: postId },
        { 
          headers: { 'X-CSRFToken': csrfToken },
          withCredentials: true
        }
      );
      const newIsLiked = response.data.status === 'liked';
      const newLikeCount = response.data.like_count;
      onLikeToggle(newIsLiked, newLikeCount);
    } catch (error) {
      alert('좋아요를 업데이트하는데 실패했습니다.');
    }
  };

  return (
    <div className='main-container__post-list-item-i-like' onClick={handleLike}>
      <img src={isLiked ? filledHeart : emptyHeart} alt="like" />
      <p>{likeCount}</p>
    </div>
  );
};

const PostForm = ({ post, formatDate }) => {
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [isLiked, setIsLiked] = useState(post.is_liked);

  const handleLikeToggle = useCallback((liked, newCount) => {
    setIsLiked(liked);
    setLikeCount(newCount);
  }, []);

  return (
    <Link to={`/feed/posts/${post.id}`} className="main-container__post-link">
      <li key={post.id} className="main-container__post-list-item">
        <div className='main-container__post-list-item-profile'>
          <Link to={`/profile/${post.user.username}`}><img src={post.user.profile_pic} alt="" /></Link>
          <div className='main-container__post-list-item-profile-name'>
            <Link to={`/profile/${post.user.username}`}><p className='nickname'>{post.user.nickname}</p></Link>
            <p className='username'>@{post.user.username}</p>
          </div>
        </div>
        <div className='main-container__post-list-item-inner'>
          <p className='main-container__post-list-item-content'>
            <TruncateText text={post.content} maxLength={200} />
          </p>
          {post.images && post.images.length > 0 && (
            <div className={`main-container__post-list-item-images images-count-${post.images.length}`}>
              {post.images.slice(0, 4).map((image, index) => (
                <div key={index} className="image-wrapper">
                  <img 
                    src={image.image} 
                    alt={`Post image ${index + 1}`} 
                    className="main-container__post-list-item-image"
                  />
                </div>
              ))}
            </div>
          )}
          
          <div className='main-container__post-list-item-i'>
            <div className='main-container__post-list-item-i-comment'>
              <img src={comment} alt="comment" />
              <p>{post.comments_count}</p>
            </div>
            <div className='main-container__post-list-item-i-view'>
              <img src={view} alt="view" />
              <p>{post.view_count}</p>
            </div>
            <LikeButton 
              postId={post.id} 
              likeCount={likeCount} 
              isLiked={isLiked} 
              onLikeToggle={handleLikeToggle}
            />
          </div>
          <div className='date-school'>
            <p className='main-container__post-list-item-date'>{formatDate(post.timestamp)}</p>
          </div>
        </div>
      </li>
    </Link>
  );
};

export default PostForm;