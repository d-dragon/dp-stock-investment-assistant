import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import WebSocketTest from './components/WebSocketTest';

// Interface definitions
interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

interface Command {
  command: string;
  description: string;
  example?: string;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [commands, setCommands] = useState<Command[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [currentTab, setCurrentTab] = useState<'chat' | 'websocket-test'>('chat');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const API_BASE_URL = 'http://localhost:5000';

  useEffect(() => {
    // Add welcome message
    addMessage('system', 'Welcome to DP Stock Investment Assistant! Please start the backend server first.');
    loadCommands();
    loadConfig();
    checkConnection();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (type: 'user' | 'assistant' | 'system', content: string, timestamp?: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: timestamp || new Date().toISOString(),
      isStreaming: false
    };
    setMessages((prev: Message[]) => [...prev, newMessage]);
  };

  const checkConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      if (response.ok) {
        setIsConnected(true);
        addMessage('system', '✅ Connected to backend server!');
      }
    } catch (error) {
      setIsConnected(false);
      addMessage('system', '❌ Backend server not available. Please start it first.');
    }
  };

  const loadCommands = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/commands`);
      if (response.ok) {
        const data = await response.json();
        setCommands(data.commands);
      }
    } catch (error) {
      console.error('Failed to load commands:', error);
      // Set default commands if server is not available
      setCommands([
        {
          command: 'help',
          description: 'Show available commands'
        },
        {
          command: 'stock analysis',
          description: 'Ask questions about specific stocks',
          example: 'What is the current price of AAPL?'
        },
        {
          command: 'market trends',
          description: 'Get insights about market trends',
          example: 'How is the tech sector performing?'
        }
      ]);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config`);
      if (response.ok) {
        const config = await response.json();
        console.log('Backend configuration loaded:', config);
        // You can use this config data to customize the frontend behavior
        // For example: update API timeouts, feature flags, etc.
      }
    } catch (error) {
      console.error('Failed to load backend config:', error);
      // Config loading is optional, so we don't show user errors
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    addMessage('user', userMessage);
    setIsLoading(true);
    setError(null);

    // Create placeholder message for streaming response
    const assistantMessageId = Date.now().toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true
    };
    setMessages((prev: Message[]) => [...prev, assistantMessage]);

    try {
      // Try streaming first
      console.log('🚀 Starting streaming request for:', userMessage);
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage, stream: true }),
      });

      console.log('📡 Response status:', response.status, response.statusText);
      console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Streaming not supported');
      }

      const decoder = new TextDecoder();
      let fullResponse = '';
      let chunkCount = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('🏁 Streaming completed. Total chunks processed:', chunkCount);
          break;
        }

        const chunk = decoder.decode(value);
        console.log('📦 Raw chunk received:', chunk);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            console.log('📋 Processing data line:', data);
            if (data === '[DONE]') {
              console.log('✅ Received completion signal');
              // Mark streaming as complete
              setMessages((prev: Message[]) => prev.map((msg: Message) => 
                msg.id === assistantMessageId 
                  ? { ...msg, isStreaming: false }
                  : msg
              ));
              return;
            }
            try {
              const parsed = JSON.parse(data);
              console.log('🔍 Parsed chunk data:', parsed);
              if (parsed.chunk) {
                chunkCount++;
                fullResponse += parsed.chunk;
                console.log('💬 Updated response length:', fullResponse.length);
                // Update the assistant message with new content
                setMessages((prev: Message[]) => prev.map((msg: Message) => 
                  msg.id === assistantMessageId 
                    ? { ...msg, content: fullResponse }
                    : msg
                ));
              }
            } catch (e) {
              console.warn('⚠️ Failed to parse chunk:', data, e);
              // Ignore parsing errors for malformed chunks
            }
          }
        }
      }

      // Mark streaming as complete if loop exits normally
      setMessages((prev: Message[]) => prev.map((msg: Message) => 
        msg.id === assistantMessageId 
          ? { ...msg, isStreaming: false }
          : msg
      ));

    } catch (error) {
      console.error('❌ Streaming error:', error);
      
      // Fallback to non-streaming
      console.log('🔄 Falling back to non-streaming mode');
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage, stream: false }),
        });

        console.log('📡 Fallback response status:', response.status);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('📄 Fallback response data:', data);
        
        // Update the assistant message with full response
        setMessages((prev: Message[]) => prev.map((msg: Message) => 
          msg.id === assistantMessageId 
            ? { ...msg, content: data.response || data.message || 'No response received', timestamp: data.timestamp, isStreaming: false }
            : msg
        ));
        
      } catch (fallbackError) {
        console.error('❌ Fallback error:', fallbackError);
        setError('Failed to connect to backend server. Make sure it\'s running on http://localhost:5000');
        
        // Remove the placeholder message on error
        setMessages((prev: Message[]) => prev.filter((msg: Message) => msg.id !== assistantMessageId));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const insertExampleQuery = (example: string) => {
    setInputValue(example);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getMessageStyle = (type: string) => {
    switch (type) {
      case 'user': return { backgroundColor: '#e3f2fd', borderLeft: '4px solid #1976d2' };
      case 'assistant': return { backgroundColor: '#f1f8e9', borderLeft: '4px solid #388e3c' };
      case 'system': return { backgroundColor: '#fff3e0', borderLeft: '4px solid #f57c00' };
      default: return { backgroundColor: '#f5f5f5', borderLeft: '4px solid #757575' };
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: '#1976d2', 
        color: 'white', 
        padding: '1rem 2rem', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between' 
      }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>📈 DP Stock Investment Assistant</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ 
            padding: '0.25rem 0.5rem', 
            borderRadius: '4px', 
            backgroundColor: isConnected ? '#4caf50' : '#f44336',
            fontSize: '0.8rem'
          }}>
            {isConnected ? '✅ Connected' : '❌ Disconnected'}
          </span>
          <button 
            onClick={checkConnection}
            style={{ 
              padding: '0.5rem 1rem', 
              backgroundColor: 'transparent', 
              border: '1px solid white', 
              borderRadius: '4px', 
              color: 'white',
              cursor: 'pointer'
            }}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        borderBottom: '1px solid #ddd',
        display: 'flex',
        padding: '0 2rem'
      }}>
        <button
          onClick={() => setCurrentTab('chat')}
          style={{
            padding: '1rem 2rem',
            backgroundColor: currentTab === 'chat' ? 'white' : 'transparent',
            border: 'none',
            borderBottom: currentTab === 'chat' ? '2px solid #1976d2' : '2px solid transparent',
            cursor: 'pointer',
            fontWeight: currentTab === 'chat' ? 'bold' : 'normal',
            color: currentTab === 'chat' ? '#1976d2' : '#666'
          }}
        >
          💬 Chat
        </button>
        <button
          onClick={() => setCurrentTab('websocket-test')}
          style={{
            padding: '1rem 2rem',
            backgroundColor: currentTab === 'websocket-test' ? 'white' : 'transparent',
            border: 'none',
            borderBottom: currentTab === 'websocket-test' ? '2px solid #1976d2' : '2px solid transparent',
            cursor: 'pointer',
            fontWeight: currentTab === 'websocket-test' ? 'bold' : 'normal',
            color: currentTab === 'websocket-test' ? '#1976d2' : '#666'
          }}
        >
          🔌 WebSocket Test
        </button>
      </div>

      {/* Tab Content */}
      {currentTab === 'websocket-test' ? (
        <div style={{ flex: 1, overflow: 'auto' }}>
          <WebSocketTest />
        </div>
      ) : (
        <>
          {/* Error Display */}
          {error && (
            <div style={{
              backgroundColor: '#ffebee',
              border: '1px solid #f44336',
              color: '#c62828',
              padding: '1rem',
              margin: '1rem 2rem',
              borderRadius: '4px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>{error}</span>
              <button 
                onClick={() => setError(null)}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: '#c62828', 
                  fontSize: '1.2rem', 
                  cursor: 'pointer' 
                }}
              >
                ×
              </button>
            </div>
          )}

          {/* Chat Area */}
          <div style={{ flex: 1, display: 'flex', gap: '1rem', padding: '1rem' }}>
            <div style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              border: '1px solid #ddd', 
              borderRadius: '8px',
              backgroundColor: 'white'
            }}>
              {/* Messages */}
              <div style={{ 
                flex: 1, 
                overflow: 'auto', 
                padding: '1rem',
                maxHeight: 'calc(100vh - 200px)'
          }}>
            {messages.map((message: Message) => (
              <div key={message.id} style={{ 
                marginBottom: '1rem',
                padding: '1rem',
                borderRadius: '8px',
                ...getMessageStyle(message.type)
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.5rem', 
                  marginBottom: '0.5rem',
                  fontSize: '0.8rem',
                  fontWeight: 'bold'
                }}>
                  <span style={{ 
                    textTransform: 'uppercase',
                    color: message.type === 'user' ? '#1976d2' : 
                           message.type === 'assistant' ? '#388e3c' : '#f57c00'
                  }}>
                    {message.type}
                  </span>
                  {message.isStreaming && (
                    <span style={{ 
                      color: '#388e3c',
                      fontSize: '0.7rem',
                      fontWeight: 'normal',
                      fontStyle: 'italic'
                    }}>
                      ✨ streaming...
                    </span>
                  )}
                  <span style={{ color: '#666' }}>
                    {formatTimestamp(message.timestamp)}
                  </span>
                </div>
                <div style={{ 
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  lineHeight: '1.5'
                }}>
                  {message.content}
                  {message.isStreaming && (
                    <span style={{ 
                      color: '#388e3c',
                      animation: 'blink 1s infinite'
                    }}>
                      ▋
                    </span>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                padding: '1rem',
                fontStyle: 'italic',
                color: '#666'
              }}>
                <span>⏳</span>
                Assistant is thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Error Alert */}
          {error && (
            <div style={{ 
              margin: '1rem',
              padding: '1rem',
              backgroundColor: '#ffebee',
              border: '1px solid #f44336',
              borderRadius: '4px',
              color: '#c62828'
            }}>
              ❌ {error}
              <button 
                onClick={() => setError(null)}
                style={{ 
                  float: 'right',
                  background: 'none',
                  border: 'none',
                  fontSize: '1.2rem',
                  cursor: 'pointer',
                  color: '#c62828'
                }}
              >
                ×
              </button>
            </div>
          )}

          {/* Input Area */}
          <div style={{ 
            padding: '1rem',
            borderTop: '1px solid #ddd',
            display: 'flex',
            gap: '0.5rem'
          }}>
            <textarea
              style={{
                flex: 1,
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                resize: 'vertical',
                minHeight: '40px',
                maxHeight: '120px',
                fontFamily: 'inherit'
              }}
              placeholder="Ask about stocks, market trends, or investment advice..."
              value={inputValue}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: isLoading || !inputValue.trim() ? '#ccc' : '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading || !inputValue.trim() ? 'not-allowed' : 'pointer',
                fontWeight: 'bold'
              }}
              onClick={sendMessage}
              disabled={isLoading || !inputValue.trim()}
            >
              {isLoading ? '⏳' : '📤'} Send
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div style={{ 
          width: '300px', 
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '1rem',
          backgroundColor: 'white',
          overflow: 'auto'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#1976d2' }}>📋 Available Commands</h3>
          
          {commands.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {commands.map((command: Command, index: number) => (
                <div key={index} style={{ 
                  padding: '0.75rem',
                  border: '1px solid #e0e0e0',
                  borderRadius: '6px',
                  backgroundColor: '#fafafa'
                }}>
                  <div style={{ 
                    fontWeight: 'bold',
                    color: '#1976d2',
                    marginBottom: '0.25rem'
                  }}>
                    {command.command}
                  </div>
                  <div style={{ 
                    fontSize: '0.9rem',
                    color: '#666',
                    marginBottom: command.example ? '0.5rem' : '0'
                  }}>
                    {command.description}
                  </div>
                  {command.example && (
                    <div style={{ 
                      fontSize: '0.8rem',
                      color: '#888',
                      fontStyle: 'italic',
                      cursor: 'pointer',
                      padding: '0.25rem',
                      backgroundColor: '#f0f0f0',
                      borderRadius: '3px',
                      border: '1px dashed #ccc'
                    }}
                    onClick={() => insertExampleQuery(command.example!)}
                    title="Click to use this example"
                    >
                      💡 {command.example}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center',
              color: '#666',
              padding: '2rem',
              fontStyle: 'italic'
            }}>
              No commands available. Please check server connection.
            </div>
          )}

          <div style={{ 
            marginTop: '1.5rem',
            padding: '1rem',
            backgroundColor: '#f8f9fa',
            borderRadius: '6px',
            fontSize: '0.85rem',
            color: '#666'
          }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1976d2' }}>ℹ️ Tips</h4>
            <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
              <li>Ask specific questions about stocks (e.g., "AAPL price")</li>
              <li>Request market analysis for sectors</li>
              <li>Get investment advice and strategies</li>
              <li>Use examples by clicking on them</li>
            </ul>
          </div>
        </div>
      </div>
        </>
      )}
    </div>
  );
};

export default App;
