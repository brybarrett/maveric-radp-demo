import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import './InputBox.css';

const InputBox = forwardRef(({ onSendMessage, disabled }, ref) => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef(null);

  // Expose focus method to parent component
  useImperativeHandle(ref, () => ({
    focus: () => {
      textareaRef.current?.focus();
    }
  }));

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  return (
    <form className="input-box" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          className="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder="Ask a question about Maveric RADP..."
          disabled={disabled}
          rows={1}
        />
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !message.trim()}
          title="Send message (Enter)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      
      {isFocused && (
        <div className="keyboard-hints">
          <span className="hint">
            <kbd>Enter</kbd> to send
          </span>
          <span className="hint-separator">·</span>
          <span className="hint">
            <kbd>Shift</kbd> + <kbd>Enter</kbd> for new line
          </span>
          <span className="hint-separator">·</span>
          <span className="hint">
            <kbd>/</kbd> to focus
          </span>
          <span className="hint-separator">·</span>
          <span className="hint">
            <kbd>⌘K</kbd> / <kbd>Ctrl+K</kbd> for new chat
          </span>
        </div>
      )}
    </form>
  );
});

InputBox.displayName = 'InputBox';

export default InputBox;