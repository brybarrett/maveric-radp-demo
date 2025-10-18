import React from 'react';
import './LoadingState.css';

function LoadingState({ message = "Analyzing your question..." }) {
  return (
    <div className="loading-state">
      <div className="skeleton-message-bubble">
        <div className="skeleton-header">
          <div className="skeleton-avatar"></div>
          <div className="skeleton-name"></div>
        </div>
        <div className="skeleton-content">
          <div className="skeleton-line skeleton-line-long"></div>
          <div className="skeleton-line skeleton-line-medium"></div>
          <div className="skeleton-line skeleton-line-short"></div>
          <div className="skeleton-line skeleton-line-long"></div>
        </div>
      </div>
      <p className="loading-message">
        <span className="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </span>
        {message}
      </p>
    </div>
  );
}

export default LoadingState;