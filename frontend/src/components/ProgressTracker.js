import React from 'react';
import './ProgressTracker.css';

function ProgressTracker({ currentStage, stages, onStageClick }) {
  const getStageStatus = (index) => {
    if (index < currentStage) return 'completed';
    if (index === currentStage) return 'current';
    return 'upcoming';
  };

  return (
    <div className="progress-tracker">
      <div className="progress-stages">
        {stages.map((stage, index) => (
          <React.Fragment key={index}>
            <div 
              className={`progress-stage ${getStageStatus(index)}`}
              onClick={() => onStageClick && onStageClick(index)}
            >
              <div className="stage-indicator">
                {index < currentStage ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                ) : (
                  <span className="stage-number">{index + 1}</span>
                )}
              </div>
              <div className="stage-label">{stage.name}</div>
            </div>
            
            {index < stages.length - 1 && (
              <div className={`progress-connector ${index < currentStage ? 'completed' : ''}`}>
                <div className="connector-line"></div>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export default ProgressTracker;