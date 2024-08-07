import React from 'react';
import './snippets.css';

function NotFoundForm() {
  return (
    <div className="not-found-container">
      <h1 className="not-found-title">404 Not Found</h1>
      <p className="not-found-description">요청하신 페이지를 찾을 수 없습니다.</p>
    </div>
  );
}

export default NotFoundForm;
