import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import './App.css';
import { debounce, measurePerformance } from './utils/performance';
import { FormattedMessage } from './components/MessageFormatter';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Optimize scroll function with useCallback
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Debounced scroll to prevent excessive calls
  const debouncedScrollToBottom = useMemo(
    () => debounce(scrollToBottom, 100),
    [scrollToBottom]
  );

  useEffect(() => {
    debouncedScrollToBottom();
  }, [messages, debouncedScrollToBottom]);

  useEffect(() => {
    // Check if backend is available with performance monitoring
    measurePerformance('Initial connection check', () => {
      checkConnection();
    });
  }, []);

  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/health');
      setIsConnected(response.ok);
    } catch (error) {
      console.error('Connection failed:', error);
      setIsConnected(false);
    }
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {

        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputValue })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const assistantMessage = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error while processing your request. Please make sure the backend server is running on http://localhost:5000' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Investment Assistant</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          <button onClick={checkConnection} className="refresh-btn">↻</button>
        </div>
      </header>

      <main className="chat-container">
        <div className="chat-header">
          <div className="connection-status">
            <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></div>
          </div>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to your Stock Investment Assistant!</h2>
              <p>Ask me about stock analysis, investment strategies, or market insights.</p>
            </div>
          )}
          
          {messages.map((message, index) => (
            <FormattedMessage 
              key={index} 
              content={message.content} 
              role={message.role} 
            />
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="avatar assistant-avatar">🤖</div>
              <div className="message-content">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="input-form">
          <div className="input-container">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about stock investments..."
              className="message-input"
              rows="1"
              disabled={!isConnected || isLoading}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!isConnected || isLoading || !inputValue.trim()}
            >
              ↗
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

export default App;
