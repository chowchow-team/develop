import React, { useContext, useEffect, useState } from 'react';
import { UserContext } from '../UserContext';
import { Link, useLocation } from 'react-router-dom';
import logo from '../static/img/logo.png';
import profile from '../static/nav/profile.png';
import like from '../static/nav/like.png';
import post from '../static/nav/post.png';
import search from '../static/nav/search.png';
import home from '../static/nav/home.png';

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

    const toggleMenu = (event) => {
        event.stopPropagation();
        setIsMenuOpen(!isMenuOpen);
    };

    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (!event.target.closest('.mb-nav-menu') && !event.target.closest('.hamburger-menu')) {
                setIsMenuOpen(false);
            }
        };

        if (isMenuOpen) {
            setTimeout(() => {
                document.addEventListener('click', handleOutsideClick);
            }, 10);
        }

        return () => {
            document.removeEventListener('click', handleOutsideClick);
        };
    }, [isMenuOpen]);

    useEffect(() => {
        setIsMenuOpen(false);
    }, [location]);

    if (shouldHideNav) return null; // 네브바 숨기기

    return (
        <nav className='nav-container'>
            <div className="nav-wrapper">
                <div className={`overlay ${isMenuOpen ? 'show' : ''}`}></div>
                <Link to="/" className="nav-logo">
                    <img src={logo} alt="Logo" />
                    <div className='logo-name-wrapper'>
                        <span className="logo-name-l">
                            챠우챠우
                        </span>
                    </div>
                </Link>
                <>
                    <button className="hamburger-menu" onClick={toggleMenu}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4 18L20 18" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M4 12L20 12" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M4 6L20 6" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                    </button>
                    <div className='nav-menu'>
                        <Link to="/"><span>홈</span></Link>
                        {user && <li><Link to={`/profile/${user.username}`}><span>프로필</span></Link></li>}
                        <Link to="/setting"><span>계정관리</span></Link>
                        <Link to="/friend">
                            <span>친구관리</span>
                            {hasNotification && <span className="notification-dot"></span>}
                        </Link>
                        {user ?
                        <Link to="/logout"><span>로그아웃</span></Link>:
                        <Link to="/login"><span className='login'>로그인</span></Link>
                        }
                    </div>
                </>
            </div>
            <div className={`mb-nav-menu ${isMenuOpen ? 'open' : ''}`}>
                  <Link to="/" className="nav-logo">
                      <img src={logo} alt="Logo" />
                      <div className='logo-name-wrapper'>
                          <span className="logo-name-l">
                              챠우챠우
                          </span>
                      </div>
                  </Link>
                  <ul>
                      <li><Link to="/"><span>홈</span></Link></li>
                      {user && <li><Link to={`/profile/${user.username}`}><span>프로필</span></Link></li>}
                      <li><Link to="/setting"><span>계정관리</span></Link></li>
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
            <div className="nav-placeholder"></div>
       </nav>
    );
}

export default NavForm;
