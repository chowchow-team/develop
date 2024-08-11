import React, { useEffect, useState, useContext, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { getCookie } from '../snippets';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import comment from '../static/img/comment.png';
import view from '../static/img/statistic.png';
import { SEOMetaTag } from '../snippets';
import './main.css'

function DetailForm() {
  const { pk } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentContent, setCommentContent] = useState('');
  const { user, getUserId } = useContext(UserContext);
  const navigate = useNavigate();
  const [offset, setOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);

  const [allCommentsLoaded, setAllCommentsLoaded] = useState(false);

  const limit = 10;
  const userid = getUserId();

  const formatDate = (dateStr) => {
    const postDate = new Date(dateStr);
    const now = new Date();
    const diffSeconds = Math.round((now - postDate) / 1000);
    const diffMinutes = Math.round(diffSeconds / 60);
    const diffHours = Math.round(diffMinutes / 60);
    const diffDays = Math.round(diffHours / 24);
    const diffMonths = Math.round(diffDays / 30);
    const diffYears = Math.round(diffMonths / 12);

    if (diffSeconds < 60) return `${diffSeconds}초 전`;
    if (diffMinutes < 60) return `${diffMinutes}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 30) return `${diffDays}일 전`;
    if (diffMonths < 12) return `${diffMonths}달 전`;
    return `${diffYears}년 전`;
  };

  const handleCopyLink = async () => {
    await navigator.clipboard.writeText(window.location.href);
    alert('링크가 복사되었습니다.');
  };

  const deletePost = (e) => {
    e.preventDefault();
    if (window.confirm("정말로 삭제하시겠습니까?")) {
      const csrfToken = getCookie('csrftoken');
      axios.delete(`/api/main/post/${pk}/`, {
        headers: { 'X-CSRFToken': csrfToken },
        withCredentials: true
      })
        .then(() => {
          navigate('/');
        })
        .catch(error => {
          console.error("Error deleting the post: ", error);
        });
    }
  };

  useEffect(() => {
    const fetchPostAndComments = async () => {
      try {
        const postResponse = await axios.get(`/api/main/post/?post_id=${pk}`);
        setPost(postResponse.data);

        const commentsResponse = await axios.get(`/api/main/comment/?post_id=${pk}&limit=${limit}&offset=0`);
        setComments(commentsResponse.data.results);
        setOffset(commentsResponse.data.results.length);
        setHasMore(commentsResponse.data.next);
      } catch (error) {
        console.error("Error loading the post or comments: ", error);
      }
    };

    fetchPostAndComments();
  }, [pk]);

  useEffect(() => {
    if (user && post) {
      axios.get(`/api/main/following/check/?follower_id=${user.id}&user_id=${post.user.id}`)
        .then(response => {
          setIsFollowing(response.data.isFollowing);
        })
        .catch(error => {
          console.error("Error checking follow status: ", error);
        });
    }
  }, [user, post]);

  

  const fetchAdditionalComments = useCallback(async () => {
    if (isLoading || !hasMore || allCommentsLoaded) return;
    setIsLoading(true);
    try {
      const response = await axios.get(`/api/main/comment/?post_id=${pk}&limit=${limit}&offset=${offset}`);
      const newComments = response.data.results;
      if (newComments.length > 0) {
        setComments(prev => [...prev, ...newComments]);
        setOffset(prev => prev + newComments.length);
        setHasMore(response.data.next);
      } else {
        setHasMore(false);
        setAllCommentsLoaded(true);
      }
    } catch (error) {
      console.error("Error fetching additional comments: ", error);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, hasMore, allCommentsLoaded, pk, limit, offset]);

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop + 1 >=
        document.documentElement.scrollHeight &&
        !isLoading &&
        hasMore &&
        !allCommentsLoaded
      ) {
        fetchAdditionalComments();
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isLoading, hasMore, allCommentsLoaded, fetchAdditionalComments]);

  const addComment = async (e) => {
    e.preventDefault();
    const csrfToken = getCookie('csrftoken');
    try {
      const response = await axios.post(`/api/main/comment/`, { 
        content: commentContent,
        post_id: pk,
        user: userid
      }, {
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        withCredentials: true
      });
      setComments(prev => [response.data, ...prev]);
      setCommentContent('');
    } catch (error) {
      console.error("Error adding a comment: ", error);
    }
  };

  const handleFollow = async () => {
    if (!user) {
      alert('로그인이 필요합니다.');
      return;
    }
    const csrfToken = getCookie('csrftoken');
    try {
      if (isFollowing) {
        await axios.post('/api/main/unfollow/request/', {
          follower_id: user.id,
          following_id: post.user.id
        }, {
          headers: { 'X-CSRFToken': csrfToken },
          withCredentials: true
        });
      } else {
        await axios.post('/api/main/follow/request/', {
          follower_id: user.id,
          following_id: post.user.id
        }, {
          headers: { 'X-CSRFToken': csrfToken },
          withCredentials: true
        });
      }
      setIsFollowing(!isFollowing);
    } catch (error) {
      console.error("Error following/unfollowing user: ", error);
    }
  };

  if (!post) return <div>Loading...</div>;

  return (
    <div className='post-detail-container'>
        <SEOMetaTag 
          title={post.content.slice(0, 20)}
          description={post.content}
          keywords='동물, 유기동물, sns, 챠우챠우'
          image={post.images && post.images.length > 0 ? post.images[0].image : 'https://chowchow.com/og_image.png'}
          url={`https://chowchow.com/posts/${pk}`}
        />
        <BackButton />
        {user?.id === post.user.id ? 
          <p className='post-detail-container__copylink' onClick={deletePost}>삭제</p>
          :
          <p className='post-detail-container__copylink' onClick={handleCopyLink}>링크복사</p>
        }
        <Link to={`/profile/${post.user.username}`}>
        <div className='post-detail-container-profile'> 
            <img src={post.user.profile_pic} alt="" />
            <div className='post-detail-container-profile-name'>
                <p className='nickname'>{post.user.nickname}</p>
                <p className='username'>@{post.user.username}</p>
            </div>
        </div>
        </Link>
        <div className='post-detail-container__content'>
          <p>{post.content}</p>
        </div>
        {post.images && post.images.length > 0 && (
          <div className={`post-detail-container__image images-count-${post.images.length}`}>
            {post.images.map((image, index) => (
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
        <div className='post-detail-container__i'>
          <div className='post-detail-container__i-comment'>
            <img src={comment} alt="comment" />
            <p>{post.comments_count}</p>
          </div>
          <div className='post-detail-container__i-view'>
            <img src={view} alt="view" />
            <p>{post.view_count}</p>
          </div>
        </div>
        <div className='date-school'>
          <p className='post-detail-container__date'>{formatDate(post.timestamp)}</p>
        </div>
        {user && user.id !== post.user.id && (
          <button onClick={handleFollow}>
            {isFollowing ? '언팔로우' : '팔로우'}
          </button>
        )}
        
        {user ? (
          <form onSubmit={addComment} className="comment-form">
            <textarea
              className="comment-textarea"
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              placeholder="댓글을 입력하세요"
            ></textarea>
            <button
              type="submit"
              className="comment-submit-btn"
              disabled={commentContent.length <= 1}
            >
              댓글 추가
            </button>
          </form>
        ) : (
          <p className='alert-comment'>* 댓글을 작성하려면 <Link to="/login">로그인</Link>해주세요.</p>
        )}
        <div className="comments-section">
          {comments.map((comment, index) => (
            <div key={`${comment.id}-${index}`} className="comment-item">
              <div className='comment-writer-profile'>
                <Link to={`/profile/${comment.user.username}`}>
                  <img src={comment.user.profile_pic} alt="" />
                </Link>
                <div className='comment-writer-profile-name'>
                  <Link to={`/profile/${comment.user.username}`}>
                    <p className='nickname'>{comment.user.nickname}</p>
                  </Link>
                  <p className='username'>@{comment.user.username}</p>
                </div>
              </div>
              <p className='content'>{comment.content}</p>
              <p className='post-detail-container__comment-time'>{formatDate(comment.timestamp)}</p>
            </div>
          ))}
        </div>
        {isLoading && <p>댓글 로딩 중...</p>}
      </div>
    );
}

export default DetailForm;