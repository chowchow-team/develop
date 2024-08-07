import React, {useState, useEffect} from 'react';
import { Link } from 'react-router-dom';
import slide1 from '../static/img/slide1.png';
import slide2 from '../static/img/slide2.png';
import bubbleText from '../static/img/bubble.svg';

function MainForm() {
    const slides = [slide1, slide2];
    const [currentSlide, setCurrentSlide] = useState(0);
    const nextSlide = () => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
    };

    useEffect(() => {
        const interval = setInterval(nextSlide, 5000);
        return () => clearInterval(interval);
    }, []);

    const goToSlide = (index) => {
        setCurrentSlide(index);
    };

    return (
        <div className='main-container'>
            <div className='img-container'>
                {slides.map((slide, index) => (
                    <img 
                        key={index} 
                        src={slide} 
                        alt={`slide-${index}`} 
                        style={{ display: index === currentSlide ? 'block' : 'none' }} 
                    />
                ))}
                <div className='carousel-buttons'>
                    {slides.map((_, index) => (
                        <button 
                            key={index} 
                            className={index === currentSlide ? 'active' : ''} 
                            onClick={() => goToSlide(index)}
                        />
                    ))}
                </div>
            </div> 
            <div className='catchp'>
                <p className='bold'><span className='color'>대학생</span>의,</p>
                <p className='bold'>대학생에 의한,</p>
                <p className='bold'>대학생을 위한</p>
                <p className='bold'>"단 하나뿐인 안전한 <span className='color'>랜덤채팅</span>"</p>
            </div>
        </div>
    );
}

export default MainForm;
