import React, { useState, useEffect } from 'react';

function PostForm({ post }) {
    return (
        <article className='post'>
            <div className='post-header'>
                <img src={post.authorAvatar} alt={post.authorName} className='author-avatar' />
                <h2>{post.authorName}</h2>
            </div>
            <p>{post.content}</p>
            {post.image && <img src={post.image} alt="Post image" className='post-image' />}
            <div className='post-actions'>
                <button>좋아요</button>
                <button>댓글</button>
                <button>공유</button>
            </div>
        </article>
    );
}

export default PostForm;