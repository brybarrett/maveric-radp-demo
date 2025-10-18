import React from 'react';
import './Sidebar.css';

function Sidebar({ collapsed, onToggle, onNewConversation, onSendMessage }) {
  const client = process.env.REACT_APP_CLIENT || 'docbot';

  const handleNavigation = (section) => {
    switch(section) {
      case 'home':
        onNewConversation();
        break;
      case 'guided-tour':
        onNewConversation(); // Resets to welcome screen with tour
        break;
      case 'ask-now':
        // Just close any active tour, stay in chat mode
        if (onSendMessage) {
          // Focus the input box (user can type immediately)
          document.querySelector('.message-input')?.focus();
        }
        break;
      case 'api':
        if (onSendMessage) {
          onSendMessage('Show me the complete API reference documentation for Maveric RADP');
        }
        break;
      case 'quickstart':
        if (onSendMessage) {
          onSendMessage('Give me a quick start guide for getting started with Maveric RADP. What are the first steps?');
        }
        break;
      default:
        break;
    }
  };

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-container">
          {!collapsed && (
            <>
              <div className="logo-text">
                <span className="logo-brand">MAVERIC</span>
                <span className="logo-subtitle">RADP</span>
              </div>
            </>
          )}
          {collapsed && <span className="logo-icon">M</span>}
        </div>
        <button className="sidebar-toggle" onClick={onToggle} title={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {/* PRIMARY ACTIONS */}
        <div className="nav-section">
          {!collapsed && <div className="nav-section-label">Navigation</div>}
          
          <button 
            className="nav-item" 
            onClick={() => handleNavigation('home')} 
            title="Home"
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            {!collapsed && <span className="nav-label">Home</span>}
          </button>

          <button 
            className="nav-item" 
            onClick={() => handleNavigation('guided-tour')} 
            title="Start Guided Tour"
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5"></path>
              <path d="M2 12l10 5 10-5"></path>
            </svg>
            {!collapsed && <span className="nav-label">Guided Tour</span>}
          </button>

          <button 
            className="nav-item nav-item-primary" 
            onClick={() => handleNavigation('ask-now')} 
            title="Ask a Question Now"
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            {!collapsed && (
              <span className="nav-label">
                Ask Now
                <span className="nav-shortcut">/</span>
              </span>
            )}
          </button>
        </div>

        {/* RESOURCES */}
        <div className="nav-section">
          {!collapsed && <div className="nav-section-label">Resources</div>}
          
          <button 
            className="nav-item" 
            onClick={() => handleNavigation('api')} 
            title="API Reference"
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            {!collapsed && <span className="nav-label">API Reference</span>}
          </button>
          
          <button 
            className="nav-item" 
            onClick={() => handleNavigation('quickstart')} 
            title="Quick Start Guide"
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            {!collapsed && <span className="nav-label">Quick Start</span>}
          </button>
        </div>

        {/* NEW CONVERSATION */}
        <div className="nav-section">
          <button 
            className="nav-item nav-item-accent" 
            onClick={onNewConversation} 
            title="New Conversation (⌘K)"
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            {!collapsed && (
              <span className="nav-label">
                New Conversation
                <span className="nav-shortcut">⌘K</span>
              </span>
            )}
          </button>
        </div>
      </nav>

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="footer-info">
            <span className="footer-label">Powered by</span>
            <span className="footer-brand">LF Connectivity</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sidebar;