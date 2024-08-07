import React, { useEffect, useState, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getCookie } from '../snippets';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import view from '../static/img/view.png';
import comment from '../static/img/comment.png';
import { SEOMetaTag } from '../snippets';

function CDetailForm() {
  const { pk } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentContent, setCommentContent] = useState('');
  const { user } = useContext(UserContext);
  const navigate = useNavigate();
  const maskUsername = (username) => {
    return username.length > 2 ? `${username.substring(0, 2)}${'*'.repeat(username.length - 2)}` : username;
  };
  const extractSEOKeywords = (titleText) => {
    if (!titleText) return '커뮤니티, 몽글몽글, 대학교, 랜덤채팅';
    const words = titleText.split(' ');
    const filteredText = words.filter(word => word.length >= 2 && !/\d/.test(word));
    if (filteredText.length === 0) return '커뮤니티, 몽글몽글, 대학교, 랜덤채팅';
    const extractedSEOKeywords = filteredText.join(', ');
    return `${extractedSEOKeywords}, 커뮤니티, 몽글몽글, 대학교, 랜덤채팅 `;
  };

  const formatDate = (dateStr) => {
      const postDate = new Date(dateStr);
      const now = new Date();
      const diffSeconds = Math.round((now - postDate) / 1000);
      const diffMinutes = Math.round(diffSeconds / 60);
      const diffHours = Math.round(diffMinutes / 60);
      const diffDays = Math.round(diffHours / 24);
      const diffMonths = Math.round(diffDays / 30);
      const diffYears = Math.round(diffMonths / 12);

      if (diffSeconds < 60) {
          return `${diffSeconds}초 전`;
      } else if (diffMinutes < 60) {
          return `${diffMinutes}분 전`;
      } else if (diffHours < 24) {
          return `${diffHours}시간 전`;
      } else if (diffDays < 30) {
          return `${diffDays}일 전`;
      } else if (diffMonths < 12) {
          return `${diffMonths}달 전`;
      } else {
          return `${diffYears}년 전`;
      }
  };

  const handleCopyLink = async () => {
    await navigator.clipboard.writeText(window.location.href);
  };
  const deletePost = (e) => {
    e.preventDefault();
    const isConfirmed = window.confirm("정말로 삭제하시겠습니까?");

    if (isConfirmed) {
      const csrfToken = getCookie('csrftoken');
      axios.delete(`/api/community/posts/${pk}/delete`, {
        headers: {
          'X-CSRFToken': csrfToken,
        },
        withCredentials: true
      })
        .then(response => {
          setPost(null);
          navigate('/community');
        })
        .catch(error => {
          console.error("Error deleting the post: ", error);
        });
    }
  };
  
  // infinitescroll
  const [offset, setOffset] = useState(0);
  const limit = 10;
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    const fetchPostAndComments = async () => {
      try {
        const postResponse = await axios.get(`/api/community/posts/${pk}/`);
        setPost(postResponse.data);

        const commentsResponse = await axios.get(`/api/community/posts/${pk}/comments/?limit=${limit}&offset=0`);
        setComments(commentsResponse.data.results);
        setOffset(commentsResponse.data.results.length);
        setHasMore(commentsResponse.data.results.length === limit);
      } catch (error) {
        console.error("Error loading the post or comments: ", error);
      }
    };

    fetchPostAndComments();
  }, [pk]);

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop + 100 >= document.documentElement.scrollHeight && !isLoading && hasMore) {
        fetchAdditionalComments();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isLoading, hasMore, offset]);

  const fetchAdditionalComments = async () => {
    if (isLoading || !hasMore) return;
    setIsLoading(true);

    try {
      const response = await axios.get(`/api/community/posts/${pk}/comments/?limit=${limit}&offset=${offset}`);
      const newComments = response.data.results;
      if (newComments.length > 0) {
        setComments(prev => [...prev, ...newComments]);
        setOffset(prev => prev + newComments.length);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error("Error fetching additional comments: ", error);
    } finally {
      setIsLoading(false);
    }
  };

  const addComment = async (e) => {
    e.preventDefault();
    const csrfToken = getCookie('csrftoken');

    try {
      const response = await axios.post(`/api/community/posts/${pk}/comments/create/`, { content: commentContent }, {
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        withCredentials: true
      });

      setComments(prev => [...prev, response.data]);
      setCommentContent('');
    } catch (error) {
      console.error("Error adding a comment: ", error);
    }
  };
  console.log(post);
  const SEOImage = post && post.images && post.images.length > 0 ? post.images[0].image : 'https://mongles.com/og_image.png';
  const SEOUrl = `https://mongles.com/community/post/${pk}`;
  const SEOKeywords = extractSEOKeywords(post ? post.title : '');
  const truncate = (str, n=150) => {
      return str?.length > n ? str.substr(0, n - 1) : str;
  };

  if (!post) return <div>Loading...</div>;

  return (
    <div className='post-detail-container'>
      <SEOMetaTag 
          title={post.title}
          description={truncate(post.content)}
          keywords={SEOKeywords}
          image={SEOImage}
          url={SEOUrl}
      />
      <BackButton/>
      {user?.username === post.user?.username ? 
          <p className='post-detail-container__copylink' onClick={deletePost}>삭제</p>
        :
          <p className='post-detail-container__copylink' onClick={handleCopyLink}>링크복사</p>
      }
      <p className='post-detail-container__title'>{post.title}</p>
      <div className='post-detail-container__writer'>
      <p className='post-detail-container__writer-school'>
        {post.user.username === 'jeff721' ? '관리자' : post.user.school_name}
      </p>
        <p className='post-detail-container__writer-username'>· {maskUsername(post.user.username)}</p>
      </div>
      <div className='post-detail-container__i'>
        <div className='post-detail-container__i-view'>
          <img src={view} alt="view"/>
          <p>{post.view_count}</p>
        </div>
        <div className='post-detail-container__i-comment'>
          <img src={comment} alt="comment"/>
          <p>{post.comments_count}</p>
        </div>
      </div>
      <div className='post-detail-container__content'>
        <p>{post.content}</p>
      </div>
      <div className='post-detail-container__image'>
          {post.images && post.images.map((image, index) => (
              <img key={index} src={image.image} alt={`Post Image ${index}`} />
          ))}
      </div>
      
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
            disabled={commentContent.length <= 1} // 댓글 내용이 1글자 이하인 경우 버튼 비활성화
          >
            댓글 추가
          </button>
        </form>
      ) : (
        <p className='alert-comment'>* 댓글을 작성하려면 <a href="/login">로그인</a>해주세요.</p>
      )}
      <div className="comments-section">
        {comments.map((comment, index) => (
          <div key={`${comment.id}-${index}`} className="comment-item">
            <div className='post-detail-container__writer'>
              <p className='post-detail-container__writer-school'>{comment.user.school_name}</p>
              <p className='post-detail-container__writer-username'>· {maskUsername(comment.user.username)}</p>
              {post.user.username === comment.user.username ? 
              <p className='post-detail-container__writer-username-checkiswriter'>작성자</p> 
              : null}
            </div>
            <p>{comment.content}</p>
            <p className='post-detail-container__comment-time'>{formatDate(comment.created_at)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CDetailForm;
