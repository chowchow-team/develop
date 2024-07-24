import React from 'react';

function URLManagement(type = 'http') {
    const protocol = type === 'http' ? 'http' : 'ws';
    const devBaseURL = `${protocol}://localhost:8000`; // 개발 환경
    const prodBaseURL = `${protocol}://mongles.com`; // 프로덕션 환경

    return process.env.NODE_ENV === 'development' ? devBaseURL : prodBaseURL;
}

export default URLManagement;