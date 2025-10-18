import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from './Sidebar';
import MessageBubble from './MessageBubble';
import InputBox from './InputBox';
import ThemeToggle from './ThemeToggle';
import GuidedTour from './GuidedTour';
import LoadingState from './LoadingState';
import './Dashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showGuidedTour, setShowGuidedTour] = useState(true);
  
  const messagesEndRef = useRef(null);
  const inputBoxRef = useRef(null);

  // Initialize session
  useEffect(() => {
    const storedSessionId = localStorage.getItem('docbot_session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      loadHistory(storedSessionId);
    } else {
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      localStorage.setItem('docbot_session_id', newSessionId);
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyboardShortcuts = (e) => {
      // Cmd+K or Ctrl+K - New conversation
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        handleNewConversation();
      }
      
      // / - Focus input (unless already focused or in an input field)
      if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        e.preventDefault();
        if (inputBoxRef.current) {
          inputBoxRef.current.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyboardShortcuts);
    return () => document.removeEventListener('keydown', handleKeyboardShortcuts);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadHistory = async (sid) => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/chat/history/${sid}`);
      if (response.data && response.data.messages && response.data.messages.length > 0) {
        const formattedMessages = response.data.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          sources: msg.sources,
          visualization: msg.visualization
        }));
        setMessages(formattedMessages);
        setShowGuidedTour(false); // Hide tour if there's history
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Exit guided tour when user sends first message
    setShowGuidedTour(false);

    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/v1/chat`, {
        message: message,
        session_id: sessionId,
        mode: 'general_qa',
        module: selectedModule
      });

      const botMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        sources: response.data.sources,
        visualization: response.data.visualization,
        suggestions: response.data.suggestions
      };
      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: `**Error Processing Request**\n\nWe encountered an issue processing your request. This could be due to:\n\n- Temporary connectivity issues\n- Server maintenance\n- Invalid request format\n\n**What to try:**\n1. Check your internet connection\n2. Retry your request\n3. Try rephrasing your question\n4. Start a new conversation (⌘K / Ctrl+K)\n\nIf the issue persists, please contact technical support.\n\n*Timestamp: ${new Date().toISOString()}*`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleExitTour = () => {
    setShowGuidedTour(false);
  };

  const handleNewConversation = () => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    localStorage.setItem('docbot_session_id', newSessionId);
    setMessages([]);
    setShowGuidedTour(true);
  };

  return (
    <div className="dashboard">
      <Sidebar 
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        onNewConversation={handleNewConversation}
        onSendMessage={handleSendMessage}
      />
      
      <div className={`dashboard-main ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="dashboard-header">
          <div className="header-left">
            <h1>Documentation Assistant</h1>
            <span className="status-badge">
              <span className="status-dot"></span>
              Online
            </span>
          </div>
          <div className="header-right">
            <ThemeToggle />
          </div>
        </div>

        <div className="dashboard-content">
          <div className="messages-container">
            {showGuidedTour && messages.length === 0 ? (
              <GuidedTour 
                onSendMessage={handleSendMessage}
                onExitTour={handleExitTour}
              />
            ) : (
              <>
                {messages.map((msg, index) => (
                  <MessageBubble 
                    key={index} 
                    message={msg}
                    onSuggestionClick={handleSuggestionClick}
                  />
                ))}
                
                {isLoading && <LoadingState />}
              </>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="dashboard-footer">
          <InputBox 
            ref={inputBoxRef}
            onSendMessage={handleSendMessage}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;