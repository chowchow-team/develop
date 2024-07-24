import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './account.css';
import logo from '../static/img/logo.png';
import { URLManagement, getCookie } from '../snippets';
import { SEOMetaTag } from '../snippets';

function SignupForm() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        school: '',
    });
    const [error, setError] = useState('');
    const [tempMessage, setTempMessage] = useState('');
    const [schoolItem, setSchoolItem] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const API_BASE_URL = URLManagement('http');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    useEffect(() => {
        const fetchSchools = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/get-schools/`);
                setSchoolItem(response.data);
            } catch (error) {
                console.error("학교 목록을 불러오는 데 실패했습니다.", error);
            }
        };
        fetchSchools();
    }, []);

    const handleSearchChange = (e) => {
        const value = e.target.value;
        setSearchTerm(value);

        // 숫자가 포함된 경우 경고 메시지 설정
        if (/\d/.test(value)) {
            setTempMessage("학교입력란입니다.");
            setTimeout(() => {
                setTempMessage('');
            }, 2000);
        } else {
            setTempMessage('');
        }
    };

    const filteredSchools = searchTerm.length > 0
        ? schoolItem.filter(school =>
            school.name.toLowerCase().includes(searchTerm.toLowerCase())
          )
        : [];
    
    const handleSchoolSelect = (school) => {
        setFormData({ ...formData, school: school.id }); // 선택한 학교의 ID를 formData에 설정
        setSearchTerm(school.name); // 검색창에 학교 이름 표시
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const csrfToken=getCookie('csrftoken');
        try {
            setTempMessage("인증메일을 전송중입니다. 잠시만 기다려주세요");
            const response = await axios.post(`${API_BASE_URL}/api/signup/`, formData, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                }
            });
            setTempMessage("인증메일이 전송되었습니다. 도착하지 않은 경우 스팸메일함을 확인해주세요"); // 메시지 설정
            setTimeout(() => {
                setTempMessage(''); // 2초 후 메시지 제거
            }, 10000);
            // 회원가입 성공 처리 로직
        } catch (error) {
            if (error.response && error.response.data) {
                // 서버로부터의 응답에 따라 오류 메시지 설정
                let error_msg = error.response.data;
                if (error_msg.username) {
                    setError(error_msg.username);
                } else if (error_msg.email) {
                    setError(error_msg.email);
                } else if (error_msg.password) {
                    setError(error_msg.password);
                } else if (error_msg.school) {
                    setError(error_msg.school);
                } else {
                    setError('회원가입 실패. 다시 시도해주세요.');
                }
            } else {
                setError('서버 오류가 발생했습니다. 다시 시도해주세요.');
            }
        }
    };

    const showTempMessage = (error) => {
        setTempMessage(error); // 메시지 설정
        setTimeout(() => {
            setTempMessage(''); // 2초 후 메시지 제거
        }, 1500);
    };

    useEffect(() => {
        if (error) {
            showTempMessage(error);
        }
    }, [error]);

    return (
        <div className="signup-container">
            <SEOMetaTag 
                title='몽글몽글: 회원가입'
                description='[회원가입하기] 대학생 커뮤니티 몽글몽글에서 다른 학교의 친구들을 만나보세요'
                keywords='몽글몽글, mongle, 랜덤채팅, 커뮤니티, 회원가입'
                image='https://mongles.com/og_image.png'
                url='https://mongles.com/signup/'
            />
            <div className='logo-img'>
                <img src={logo} alt="Logo" />
                <div className='logo-span'>
                    <span className='logo-s'>대학생 랜덤채팅</span>
                    <span className='logo-l'>
                        몽글몽글
                    </span>
                </div>
            </div>
            {tempMessage && <div className='error'>{tempMessage}</div>}
            <form onSubmit={handleSubmit}>
                <input
                    className="signup-input"
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="아이디"
                />
                <input
                    className="signup-input"
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="학교 이메일"
                />
                <input
                    className="signup-input"
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="비밀번호"
                />
                <input
                    className="signup-input"
                    type="text"
                    value={searchTerm}
                    onChange={handleSearchChange}
                    placeholder="학교 검색"
                />
                {searchTerm.length > 0 && filteredSchools.length > 0 ? (
                    <ul className="search-results">
                        {filteredSchools.map(school => (
                            <li
                                key={school.id}
                                onClick={() => handleSchoolSelect(school)}
                                style={{cursor: 'pointer'}}
                                className='search-item'
                            >
                                {school.name}
                            </li>
                        ))}
                    </ul>
                ): searchTerm.length > 0 && filteredSchools.length === 0 ? (
                    <ul className="search-results">
                        <li>학교 검색 결과가 없습니다.</li>
                    </ul>
                ) : null}

                <button className="signup-button" type="submit">회원가입</button>
                <p className='signup-notice'>메일전송에는 최대 3분이 소요될 수 있습니다.</p>
            </form>
            
        </div>
    );
  
}
export default SignupForm;