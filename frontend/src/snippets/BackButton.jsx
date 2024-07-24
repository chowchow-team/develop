import React from 'react';
import { useNavigate } from 'react-router-dom';
import back from '../static/img/back.png';
import './snippets.css';

function BackButton() {
  const navigate = useNavigate();

  const goBack = () => {
    navigate(-1); // 이전 페이지로 이동
  };

  return (
    <img src={back} alt="뒤로 가기" onClick={goBack} className="back-button" />
  );
}

export default BackButton;
