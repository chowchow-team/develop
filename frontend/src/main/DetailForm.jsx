import React, { useEffect, useState, useContext, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { getCookie } from '../snippets';
import { UserContext } from '../UserContext';
import { BackButton } from '../snippets';
import comment from '../static/img/comment.png';
import view from '../static/img/statistic.png';
import downloadIcon from '../static/img/download.png';
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
  const [filename, setFilename] = useState('');


  const [file, setFile] = useState(null);

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

  const decodeKoreanFilename = (url) => {
    try {
      // URL에서 파일명 부분만 추출
      let encodedFilename = url.split('/').pop();
      
      // 반복적으로 디코딩 시도
      let decodedFilename = encodedFilename;
      let prevDecodedFilename;
      do {
        prevDecodedFilename = decodedFilename;
        decodedFilename = decodeURIComponent(prevDecodedFilename.replace(/\+/g, ' '));
      } while (decodedFilename !== prevDecodedFilename);
      
      // 파일명에서 확장자 앞의 언더스코어와 랜덤 문자열 제거
      const cleanedFilename = decodedFilename.replace(/_[^.]+(\.[^.]+)$/, '$1');
      
      return cleanedFilename;
    } catch (error) {
      console.error('파일명 디코딩 중 오류 발생:', error);
      return url.split('/').pop(); // 디코딩에 실패한 경우 원본 파일명 반환
    }
  };

  const extractFilenameFromUrl = (url) => {
    try {
      // Extract the part after '/media/post_files/'
      const regex = /\/media\/post_files\/(.+)$/;
      const match = url.match(regex);
      
      if (!match) {
        throw new Error('Invalid URL format');
      }
      
      const filenamePart = match[1];
      
      // Extract the encoded filename (remove the code part)
      const encodedFilename = filenamePart.replace(/^[^_]+_/, '');
      
      // Decode the filename
      let decodedFilename = encodedFilename;
      let prevDecodedFilename;
      do {
        prevDecodedFilename = decodedFilename;
        decodedFilename = decodeURIComponent(prevDecodedFilename.replace(/\+/g, ' '));
      } while (decodedFilename !== prevDecodedFilename);
      
      // Remove the file extension
      const cleanedFilename = decodedFilename.replace(/\.[^/.]+$/, '');
      
      return cleanedFilename;
    } catch (error) {
      console.error('파일명 추출 및 디코딩 중 오류 발생:', error);
      return url.split('/').pop(); // 실패 시 원본 파일명 반환
    }
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
          alert('게시물 삭제에 실패했습니다.');
        });
    }
  };

  useEffect(() => {
    const fetchPostAndComments = async () => {
      try {
        const postResponse = await axios.get(`/api/main/post/?post_id=${pk}`);
        setPost(postResponse.data);
        setFile(postResponse.data.file);

        const commentsResponse = await axios.get(`/api/main/comment/?post_id=${pk}&limit=${limit}&offset=0`);
        setComments(commentsResponse.data.results);
        setOffset(commentsResponse.data.results.length);
        setHasMore(commentsResponse.data.next);
      } catch (error) {
        alert('게시물을 불러오는데 실패했습니다.');
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
          alert('팔로우 상태를 불러오는데 실패했습니다.');
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
      alert('댓글을 불러오는데 실패했습니다.');
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
      alert('댓글을 추가하는데 실패했습니다.');
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
      alert('팔로우 상태를 업데이트하는데 실패했습니다.');
    }
  };

  const handleDownload = async () => {
    if (!file) return;
    try {
      const response = await axios.get(`/api/main/post/?post_id=${pk}&download=true`, {
        responseType: 'blob',
      });
      // Content-Disposition 헤더에서 파일 이름 추출
      const contentDisposition = response.headers['content-disposition'];
      let fileName = 'download';
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/i);
        if (fileNameMatch.length === 2)
          fileName = fileNameMatch[1];
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('파일 다운로드 중 오류 발생:', error);
      alert('파일 다운로드에 실패했습니다.');
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
        {file && (
          <div className='post-detail-container__file'>
            <button onClick={handleDownload} className='download-button'>
              <img src={downloadIcon} alt="Download" />
              다운로드
            </button>
            <p>{extractFilenameFromUrl(post.file)}</p>
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