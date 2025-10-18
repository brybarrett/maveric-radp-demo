import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import './MessageBubble.css';

function MessageBubble({ message, onSuggestionClick }) {
  const [copiedCode, setCopiedCode] = useState(null);

  useEffect(() => {
    Prism.highlightAll();
  }, [message]);

  const copyToClipboard = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(index);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const CodeBlock = ({ node, inline, className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || '');
    const code = String(children).replace(/\n$/, '');
    const blockIndex = `${message.timestamp}-${code.substring(0, 20)}`;
    const isCopied = copiedCode === blockIndex;
    
    if (!inline && match) {
      return (
        <div className="code-block-wrapper">
          <div className="code-block-header">
            <span className="code-language">{match[1]}</span>
            <button 
              className="copy-code-btn"
              onClick={() => copyToClipboard(code, blockIndex)}
              title={isCopied ? "Copied!" : "Copy code"}
            >
              {isCopied ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Copied
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                  Copy
                </>
              )}
            </button>
          </div>
          <pre className={className}>
            <code className={className} {...props}>
              {children}
            </code>
          </pre>
        </div>
      );
    }
    
    return (
      <code className={className} {...props}>
        {children}
      </code>
    );
  };

  const renderContent = () => {
    if (message.role === 'system') {
      return (
        <div className="system-message">
          <div className="system-text">{message.content}</div>
        </div>
      );
    }

    return (
      <div className={`message-bubble ${message.role}-message`}>
        <div className="message-header">
          <span className="message-role">
            {message.role === 'user' ? 'You' : 'Assistant'}
          </span>
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>

        <div className={`message-content ${message.isError ? 'error-message' : ''}`}>
          {message.isError && (
            <div className="error-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
          )}
          <ReactMarkdown
            components={{
              code: CodeBlock
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <span className="sources-label">Sources:</span>
            {message.sources.map((source, index) => (
              <span key={index} className="source-tag">
                {source.source}
              </span>
            ))}
          </div>
        )}

        {message.suggestions && message.suggestions.length > 0 && (
          <div className="message-suggestions">
            <div className="suggestions-label">Related questions:</div>
            <div className="suggestions-grid">
              {message.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => onSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return renderContent();
}

export default MessageBubble;