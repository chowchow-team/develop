// PostForm.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function PostForm({ post }) {
    const [isLiked, setIsLiked] = useState(false);
    const [comments, setComments] = useState(post.comments || []);

    const handleLike = () => {
        setIsLiked(!isLiked);
        //좋아요api넣어야됨
    };

    const handleComment = (e) => {
        e.preventDefault();
        // 댓글api 넣어야됨
        const newComment = {
            id: Date.now(),
            user: '현재 사용자',
            content: e.target.comment.value,
            timestamp: new Date().toISOString()
        };
        setComments([...comments, newComment]);
        e.target.comment.value = '';
    };

    return (
        <div className="post">
            <div className="post-header">
                <Link to={`/profile/${post.userId}`} className="user-avatar">
                    <img src={post.userAvatar} alt={post.userName} />
                </Link>
                <div className="post-info">
                    <Link to={`/profile/${post.userId}`} className="user-name">{post.userName}</Link>
                    <span className="post-time">{new Date(post.timestamp).toLocaleString()}</span>
                </div>
            </div>
            <div className="post-content">{post.content}</div>
            {post.image && <img src={post.image} alt="Post content" className="post-image" />}
            <div className="post-actions">
                <button onClick={handleLike} className={`like-button ${isLiked ? 'liked' : ''}`}>
                    {isLiked ? '좋아요 취소' : '좋아요'}
                </button>
                <button className="comment-button">댓글</button>
                <button className="share-button">공유</button>
            </div>
            <div className="post-stats">
                <span>{post.likes + (isLiked ? 1 : 0)} 좋아요</span>
                <span>{comments.length} 댓글</span>
            </div>
            <div className="comments-section">
                {comments.map(comment => (
                    <div key={comment.id} className="comment">
                        <Link to={`/profile/${comment.userId}`} className="comment-user">{comment.user}</Link>
                        <span className="comment-content">{comment.content}</span>
                    </div>
                ))}
            </div>
            <form onSubmit={handleComment} className="comment-form">
                <input type="text" name="comment" placeholder="댓글을 입력하세요..." />
                <button type="submit">게시</button>
            </form>
        </div>
    );
}

export default PostForm;