import React, { useState } from 'react';

const TruncateText = ({ text, maxLength = 100 }) => {
    const [isExpanded, setIsExpanded] = useState(false);
  
    const toggleExpand = (e) => {
        e.preventDefault();  // 링크 이벤트 중지
        e.stopPropagation(); // 이벤트 버블링 방지용 (더보기때문에 추가함)
        setIsExpanded(!isExpanded);
    };
  
    return (
        <div className="truncate-text">
            <p>
                {isExpanded ? text : `${text.slice(0, maxLength)}${text.length > maxLength ? '...' : ''}`}
            </p>
            {text.length > maxLength && (
                <button onClick={toggleExpand} className="truncate-text__button">
                    {isExpanded ? '접기' : '더보기'}
                </button>
            )}
        </div>
    );
};

export default TruncateText;