import React from 'react';
import './snippets.css';
import { Link, useLocation } from 'react-router-dom';
import { URLManagement, useWindowSize } from '../snippets';

function FooterForm() {
  const location = useLocation();
  const hideNavOnPaths = ['/chat', '/friend', '/profile', '/login', '/test', '/signup']; // /e1i5를 제거했습니다.
  const dmPath = [/^\/dm\/[^\/]+$/];
  const { width } = useWindowSize();
  const isMobile = width < 768;

  const isDMPath = dmPath.some((regex) => location.pathname.match(regex));
  const shouldHideFooter = hideNavOnPaths.includes(location.pathname) || isDMPath || location.pathname === '/e1i5';

  if (shouldHideFooter) return null;
  return (
    <footer className="footer-container">
      <p className='main-footer'>Copyright 2024. 몽글몽글. All rights reserved.</p>
      <p className='email'>Contact: dev.mongle@gmail.com | 
      <Link to="/policy"><span> 개인정보처리방침</span></Link>
      </p>
      <p className='copyright'>Copyright Information: The image "Voxel Planet of the Little Prince / MagicaVoxel" used on this landing page is based on the work by moyicat,</p>
      <p className='copyright'>available under a Creative Commons Attribution (CC BY) license. For more details, please visit https://sketchfab.com/3d-models/voxel-planet-of-the-little-prince-magicavoxel-8a7cf90ac42c4ef693342404826c06ae.</p>
    </footer>
  );
}

export default FooterForm;
