import React, { useEffect, useRef, useState, useContext, useCallback } from 'react';
import axios from 'axios';
import { UserContext } from '../UserContext';
import robotEye from '../static/img/robot-emotion.gif';
import './E1I5Stream.css';

function E1I5Stream() {
  const { user } = useContext(UserContext);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const joystickRef = useRef(null);
  const joystickContainerRef = useRef(null);
  const [videoUrls, setVideoUrls] = useState([]);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [joystickPosition, setJoystickPosition] = useState({ x: 0, y: 0 });

  const uploadVideo = async (blob) => {
    const formData = new FormData();
    formData.append('video', blob, 'streamed_video.webm');

    try {
      const response = await axios.post('/api/e1i5/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log(response.data.message);
    } catch (error) {
      console.error('Error uploading video:', error);
    }
  };

  const startRecording = (mediaRecorder) => {
    mediaRecorder.start(4000); // 4초 간격으로 데이터 수집
    setTimeout(() => {
      mediaRecorder.stop();
    }, 4000);
  };

  const startStream = useCallback(async () => {
    const videoConstraints = {
      video: {
        facingMode: 'user' // 전면 카메라를 사용
      },
      audio: true
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(videoConstraints);

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
        console.log("Local stream set");
      }

      let options = { mimeType: 'video/webm' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'video/webm; codecs=vp8' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          options = { mimeType: '' };
        }
      }

      const mediaRecorder = new MediaRecorder(stream, options);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          console.log("Video chunk available, uploading...");
          uploadVideo(event.data);
          startRecording(mediaRecorder);
        }
      };

      startRecording(mediaRecorder);

      console.log("MediaRecorder started");
    } catch (error) {
      console.error('Error starting stream:', error);
    }
  }, []);

  const fetchLatestVideos = useCallback(async () => {
    try {
      const response = await axios.get('/api/e1i5/videos/latest/');
      setVideoUrls(response.data.video_urls);
    } catch (error) {
      console.error('Error fetching videos:', error);
    }
  }, []);

  useEffect(() => {
    if (user && user.username === 'jeff721') {
      startStream();
    } else {
      fetchLatestVideos();
    }
  }, [user, startStream, fetchLatestVideos]);

  useEffect(() => {
    const videoElement = remoteVideoRef.current;

    const handleEnded = () => {
      setTimeout(() => {
        if (videoUrls.length > 0) {
          const nextIndex = (currentVideoIndex + 1) % videoUrls.length;
          setCurrentVideoIndex(nextIndex);
          videoElement.src = videoUrls[nextIndex];
          videoElement.load();
        }
      }, 10);
    };

    const handleCanPlayThrough = () => {
      videoElement.play().catch(error => console.error('Error playing video:', error));
    };

    const handleError = async () => {
      setTimeout(async () => {
        await fetchLatestVideos();
        if (videoUrls.length > 0) {
          videoElement.src = videoUrls[currentVideoIndex];
          videoElement.load();
        }
      }, 20);
    };

    if (videoElement && videoUrls.length > 0) {
      videoElement.src = videoUrls[currentVideoIndex];
      videoElement.load();
      videoElement.addEventListener('ended', handleEnded);
      videoElement.addEventListener('canplaythrough', handleCanPlayThrough);
      videoElement.addEventListener('error', handleError);

      return () => {
        videoElement.removeEventListener('ended', handleEnded);
        videoElement.removeEventListener('canplaythrough', handleCanPlayThrough);
        videoElement.removeEventListener('error', handleError);
      };
    }
  }, [videoUrls, currentVideoIndex, fetchLatestVideos]);

  const handleJoystickMove = (event) => {
    const rect = joystickContainerRef.current.getBoundingClientRect();
    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    const clientY = event.touches ? event.touches[0].clientY : event.clientY;
    const x = clientX - rect.left - rect.width / 2;
    const y = clientY - rect.top - rect.height / 2;
    
    const distance = Math.sqrt(x * x + y * y);
    const maxDistance = rect.width / 2;

    if (distance > maxDistance) {
      setJoystickPosition({ x: 0, y: 0 });
    } else {
      setJoystickPosition({ x, y });
    }
  };

  const handleJoystickEnd = () => {
    setJoystickPosition({ x: 0, y: 0 });
  };

  return (
    <div>
      {user?.username === 'jeff721' ? (
        <div className="video-container fullscreen-video">
          <video ref={localVideoRef} autoPlay playsInline muted style={{ display: 'none' }} />
          <img src={robotEye} alt="Robot Emotion" className="fullscreen-image" />
        </div>
      ) : videoUrls.length > 0 ? (
        <div className="video-container">
          <video ref={remoteVideoRef} autoPlay playsInline muted />
          <div
            className="joystick-container"
            ref={joystickContainerRef}
            onMouseMove={handleJoystickMove}
            onMouseUp={handleJoystickEnd}
            onTouchMove={handleJoystickMove}
            onTouchEnd={handleJoystickEnd}
          >
            <div
              className="joystick"
              ref={joystickRef}
              style={{
                transform: `translate(${joystickPosition.x}px, ${joystickPosition.y}px)`
              }}
            />
          </div>
          <div className="button-container">
            <button className="control-button">밥 주기</button>
            <button className="control-button">놀이하기</button>
          </div>
        </div>
      ) : (
        <p>영상이 없습니다.</p>
      )}
    </div>
  );
}

export default E1I5Stream;
