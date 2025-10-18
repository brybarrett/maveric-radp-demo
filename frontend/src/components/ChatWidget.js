import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import MessageBubble from './MessageBubble';
import InputBox from './InputBox';
import ModeSelector from './ModeSelector';
import './ChatWidget.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ChatWidget() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [mode, setMode] = useState('full_overview');
  const [selectedModule, setSelectedModule] = useState(null);
  const [availableModes, setAvailableModes] = useState([]);
  const [showWelcome, setShowWelcome] = useState(true);
  
  const messagesEndRef = useRef(null);

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
    
    // Load available modes
    loadAvailableModes();
    
    // Add welcome message
    addWelcomeMessage();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadAvailableModes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/chat/modes`);
      setAvailableModes(response.data);
    } catch (error) {
      console.error('Failed to load modes:', error);
    }
  };

  const loadHistory = async (sid) => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/chat/history/${sid}`);
      if (response.data && response.data.messages) {
        const formattedMessages = response.data.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          sources: msg.sources,
          visualization: msg.visualization
        }));
        setMessages(formattedMessages);
        setShowWelcome(false);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const addWelcomeMessage = () => {
    const welcomeMsg = {
      role: 'assistant',
      content: `Welcome to the Maveric RADP Documentation Assistant.

**Available Interaction Modes:**
- Full Overview - Comprehensive workflow guidance from start to finish
- Module Deep-Dive - Detailed technical information on specific components
- General Q&A - Direct answers to specific questions

**Core Platform Capabilities:**
- Digital Twin training and RF prediction
- UE track generation and simulation
- Network orchestration and optimization
- xApp/rApp algorithm development

Select a mode above or ask a question to begin.`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMsg]);
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message to UI
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setShowWelcome(false);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/v1/chat`, {
        message: message,
        session_id: sessionId,
        mode: mode,
        module: selectedModule
      });

      // Add bot response to UI
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
      
      // Add error message
      const errorMessage = {
        role: 'assistant',
        content: 'An error occurred processing your request. Please try again or contact support if the issue persists.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    
    // Add system message about mode change
    const modeChangeMsg = {
      role: 'system',
      content: `Mode changed to: ${newMode.replace('_', ' ')}`,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, modeChangeMsg]);
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleNewConversation = () => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    localStorage.setItem('docbot_session_id', newSessionId);
    setMessages([]);
    addWelcomeMessage();
    setShowWelcome(true);
  };

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <div className="header-content">
          <h2>Maveric Assistant</h2>
          <span className="status-indicator">● Online</span>
        </div>
        <div className="header-actions">
          <ModeSelector 
            currentMode={mode} 
            onModeChange={handleModeChange}
            availableModes={availableModes}
          />
          <button 
            className="new-conversation-btn"
            onClick={handleNewConversation}
            title="Start New Conversation"
          >
            ↻ New
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, index) => (
          <MessageBubble 
            key={index} 
            message={msg}
            onSuggestionClick={handleSuggestionClick}
          />
        ))}
        
        {isLoading && (
          <div className="loading-indicator">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <InputBox 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  );
}

export default ChatWidget;