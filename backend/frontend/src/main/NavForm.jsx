import React, { useContext, useEffect, useState } from 'react';
import { UserContext } from '../UserContext';
import { Link, useLocation } from 'react-router-dom';
import logo from '../static/img/logo.png';
import e1i5logo from '../static/img/e1i5logo2.png';
import axios from 'axios';
import './main.css';
import { URLManagement, useWindowSize } from '../snippets';

function NavForm() {
    const { user } = useContext(UserContext);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [hasNotification, setHasNotification] = useState(false);
    const location = useLocation();
    const API_BASE_URL = URLManagement('http');
    const { width } = useWindowSize();
    const isMobile = width < 768;
    // 모바일에서 네브바 숨길 경로
    const dmPath = [/^\/dm\/[^\/]+$/];
    const hideNavOnPaths = ['/chat', '/test'];
    const isDMPath = dmPath.some((regex) => location.pathname.match(regex));
    const shouldHideNav = (hideNavOnPaths.includes(location.pathname) || isDMPath) && isMobile;

    const checkNotifications = async () => {
        if (user) {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/notification/check-notification`, { withCredentials: true });
                setHasNotification(response.data.message === "You have notifications");
            } catch (error) {
                console.error("알림 상태 확인 실패", error);
            }
        }
    };

    useEffect(() => {
        if (user) {
            checkNotifications();
        }
    }, [user, location]);

    const toggleMenu = (event) => {
        event.stopPropagation(); // 메뉴 토글 함수에서 이벤트 전파를 막습니다.
        setIsMenuOpen(!isMenuOpen);
    };

    useEffect(() => {
        // 메뉴가 열린 후 외부 클릭을 감지하기 위한 로직
        const handleOutsideClick = (event) => {
            // 클릭된 요소가 메뉴나 토글 버튼 외부인 경우 메뉴를 닫습니다.
            if (!event.target.closest('.mb-nav-menu') && !event.target.closest('.hamburger-menu')) {
                setIsMenuOpen(false);
            }
        };

        // 메뉴가 열린 경우, 외부 클릭 감지를 활성화합니다.
        if (isMenuOpen) {
            setTimeout(() => {
                document.addEventListener('click', handleOutsideClick);
            }, 10); // 메뉴가 열린 직후 외부 클릭에 의한 닫힘을 방지하기 위한 짧은 지연
        }

        // Cleanup 함수에서는 이벤트 리스너를 제거합니다.
        return () => {
            document.removeEventListener('click', handleOutsideClick);
        };
    }, [isMenuOpen]);

    useEffect(() => {
        setIsMenuOpen(false);
    }, [location]);

    if (shouldHideNav) return null; // 네브바 숨기기

    // 경로에 따른 로고 및 이름 설정
    const isE1I5Path = location.pathname.startsWith('/e1i5');
    const currentLogo = isE1I5Path ? e1i5logo : logo;
    const logoName = isE1I5Path ? 'PUP CARE' : '챠우챠우';

    return (
        <nav>
            <div className="nav-wrapper">
                <div className={`overlay ${isMenuOpen ? 'show' : ''}`}></div>
                <Link to="/" className="nav-logo">
                    <img src={currentLogo} alt="Logo" />
                    <div className='logo-name-wrapper'>
                        <span className="logo-name-l">
                            {logoName}
                        </span>
                    </div>
                </Link>
                {!isE1I5Path && (
                  <>
                    <button className="hamburger-menu" onClick={toggleMenu}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4 18L20 18" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M4 12L20 12" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M4 6L20 6" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                    </button>
                    <div className='nav-menu'>
                        <Link to="/profile"><span>프로필</span></Link>
                        <Link to="/setting"><span>계정관리</span></Link>
                        <li><Link to="/community"><span>커뮤니티</span></Link></li>
                        <Link to="/friend">
                            <span>친구관리</span>
                            {hasNotification && <span className="notification-dot"></span>}
                        </Link>
                        {user ?
                        <Link to="/logout"><span>로그아웃</span></Link>:
                        <Link to="/login"><span>로그인</span></Link>
                        }
                        <Link to="/chat"><button className="chat-button">채팅시작</button></Link>
                    </div>
                  </>
                )}
            </div>
            {!isE1I5Path && (
              <div className={`mb-nav-menu ${isMenuOpen ? 'open' : ''}`}>
                  <Link to="/" className="nav-logo">
                      <img src={currentLogo} alt="Logo" />
                      <div className='logo-name-wrapper'>
                          <span className="logo-name-l">
                              {logoName}
                          </span>
                      </div>
                  </Link>
                  <ul>
                      <li><Link to="/chat"><span>채팅시작</span></Link></li>
                      <li><Link to="/profile"><span>프로필</span></Link></li>
                      <li><Link to="/setting"><span>계정관리</span></Link></li>
                      <li><Link to="/community"><span>커뮤니티</span></Link></li>
                      <li>
                          <Link to="/friend">
                              <span>친구관리</span>
                              {hasNotification && <span className="notification-dot"></span>}
                          </Link>
                      </li>
                      {user ?
                      <li><Link to="/logout"><span>로그아웃</span></Link></li>:
                      <li><Link to="/login"><span>로그인</span></Link></li>
                      }
                  </ul>
              </div>
            )}
       </nav>
    );
}

export default NavForm;
