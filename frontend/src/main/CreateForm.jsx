import React, { useState, useContext, useEffect, useRef } from 'react';
import axios from 'axios';
import { URLManagement, getCookie } from '../snippets';
import { UserContext } from '../UserContext';
import { useNavigate } from 'react-router-dom';
import { BackButton } from '../snippets';
import redDelete from '../static/img/red-delete.png';
import camera from '../static/img/camera.png';
import fileIcon from '../static/img/file.png';

function CreateForm() {
    const [content, setContent] = useState('');
    const API_BASE_URL = URLManagement('http');
    const { user, getUserId } = useContext(UserContext);
    const navigate = useNavigate();

    const [images, setImages] = useState([]);
    const [previewImages, setPreviewImages] = useState([]);
    const [file, setFile] = useState(null);

    const imageInputRef = useRef();
    const fileInputRef = useRef();

    const userid = getUserId();

    const handleImageButtonClick = () => {
        if (images.length < 4) {
            imageInputRef.current.click();
        } else {
            alert('이미지는 최대 4개까지만 업로드할 수 있습니다.');
        }
    };

    const handleFileButtonClick = () => {
        if (!file) {
            fileInputRef.current.click();
        } else {
            alert('파일은 1개만 업로드할 수 있습니다.');
        }
    };

    const handleImageChange = (e) => {
        if (e.target.files) {
            const remainingSlots = 4 - images.length;
            const filesArray = Array.from(e.target.files).slice(0, remainingSlots);
            
            const newPreviewImages = filesArray.map(file => URL.createObjectURL(file));
    
            setPreviewImages((prevImages) => [...prevImages, ...newPreviewImages]);
            setImages((prevImages) => [...prevImages, ...filesArray]);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleRemoveImage = (indexToRemove) => {
        setPreviewImages((prevImages) => prevImages.filter((_, index) => index !== indexToRemove));
        setImages((prevImages) => prevImages.filter((_, index) => index !== indexToRemove));
    };

    const handleRemoveFile = () => {
        setFile(null);
    };

    useEffect(() => {
        const storedUser = localStorage.getItem('userData');
        if (!storedUser) {
            navigate('/login');
            return;
        }
    }, [user, navigate]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const csrfToken = getCookie('csrftoken');
        const formData = new FormData();
        formData.append('content', content);
        formData.append('user_id', userid);
        images.forEach((image, index) => {
            formData.append('images', image, image.name);
        });
        if (file) {
            formData.append('file', file, file.name);
        }
        const config = {
            headers: {
                'Content-Type': 'multipart/form-data',
                'X-CSRFToken': csrfToken,
            },
            withCredentials: true
        };

        axios.post(`${API_BASE_URL}/api/main/post/`, formData, config)
            .then(response => {
                setContent('');
                navigate('/');
            })
            .catch(error => {
                if(error.response){
                    if(error.response.status === 401){
                        alert('로그인이 필요합니다.');
                        navigate('/login');
                    } else if(error.response.status === 400){
                        alert('게시물을 작성하는데 실패했습니다.');
                    } else if(error.response.status === 500){
                        alert('파일 형식이 올바르지 않습니다.');
                    } else{
                        alert('서버와의 통신이 원활하지 않습니다.');
                    }
                }else{
                    alert('서버와의 통신이 원활하지 않습니다.');
                }   
            });
    };

    return (
        <form onSubmit={handleSubmit} className="create-container__form">
            <BackButton />
            <div className='create-container__form__total'>
                <div className="create-container__form-group content">
                    <textarea
                        id="content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder='내용을 입력하세요'
                        className="create-container__form-textarea"
                    />
                </div>
                <div className='submit-and-upload'>
                    <div className='iconbox'>
                    <div className="image-input" onClick={handleImageButtonClick}>
                        <img src={camera} alt="camera" />
                    </div>
                    <div className="file-input" onClick={handleFileButtonClick}>
                        <img src={fileIcon} alt="file" />
                    </div>
                    </div>
                    <button type="submit" className="create-container__form-submit" disabled={!content}>
                        <span>&#62;</span>
                    </button>
                </div>
            </div>
            
            <div className="create-container__form-group images">
                {previewImages.map((image, index) => (
                    <div key={index} className="image-preview-container">
                        <img src={image} alt={`preview ${index}`} />
                        <div
                        className="remove-image-icon"
                        onClick={() => handleRemoveImage(index)}>
                            <img src={redDelete} alt="remove" />
                        </div>
                    </div>
                ))}
                <input 
                    className="hidden-btn" 
                    type="file" 
                    multiple 
                    accept="image/*"
                    onChange={handleImageChange}
                    ref={imageInputRef}
                    disabled={images.length >= 4}
                />
            </div>
            {images.length >= 4 && (
                <p className="image-limit-message">이미지는 최대 4개까지만 업로드할 수 있습니다.</p>
            )}
            
            {file && (
                <div className="file-preview-container">
                    <p>{file.name}</p>
                    <div
                        className="remove-file-icon"
                        onClick={handleRemoveFile}>
                        <p> x 업로드취소</p>
                    </div>
                </div>
            )}
            <input 
                className="hidden-btn" 
                type="file" 
                onChange={handleFileChange}
                ref={fileInputRef}
                accept=".pdf,.hwp,.xlsx,.xls,.docx,.doc"
            />
        </form>
    );
}

export default CreateForm;