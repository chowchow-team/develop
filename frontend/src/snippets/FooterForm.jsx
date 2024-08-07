import React from 'react';
import './snippets.css';
import { Link, useLocation } from 'react-router-dom';
import { URLManagement, useWindowSize } from '../snippets';

function FooterForm() {
  const location = useLocation();
  const hideNavOnPaths = ['/friend', '/profile', '/login', '/signup'];
  const dmPath = [/^\/dm\/[^\/]+$/];
  const { width } = useWindowSize();
  const isMobile = width < 768;

  const isDMPath = dmPath.some((regex) => location.pathname.match(regex));
  const shouldHideFooter = hideNavOnPaths.includes(location.pathname) || isDMPath || location.pathname === '/e1i5';

  if (shouldHideFooter) return null;
  return (
    <footer className="footer-container">
      <p className='main-footer'>Copyright 2024. 챠우챠우. All rights reserved. | 
        제 11회 SW 개발보안 경진대회 출품작 (곽병혁, 김재윤)</p>
      <p className='email'>Contact: chow3mail@gmail.com</p>
    </footer>
  );
}

export default FooterForm;
