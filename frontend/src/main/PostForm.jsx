import React from 'react';
import { Link } from 'react-router-dom';
import TruncateText from './TruncateText';
import comment from '../static/img/comment.png';

const PostForm = ({ post, formatDate }) => {
  return (
    <Link to={`/feed/posts/${post.id}`} className="main-container__post-link">
      <li key={post.id} className="main-container__post-list-item">
        <div className='main-container__post-list-item-profile'>
          <img src={post.user.profile_pic} alt="" />
          <div className='main-container__post-list-item-profile-name'>
            <p className='nickname'>{post.user.nickname}</p>
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