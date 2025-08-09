import React, { useState, useEffect } from 'react';
import { webSocketService } from '../services/webSocketService';

const WebSocketTest: React.FC = () => {
  const [connectionState, setConnectionState] = useState('disconnected');
  const [messages, setMessages] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Set up event listeners
    webSocketService.onConnect(() => {
      console.log('WebSocket connected in component');
      setConnectionState('connected');
      setError(null);
      addMessage('System: Connected to WebSocket server');
    });

    webSocketService.onDisconnect((reason: string) => {
      console.log('WebSocket disconnected in component:', reason);
      setConnectionState('disconnected');
      addMessage(`System: Disconnected - ${reason}`);
    });

    webSocketService.onMessage((data) => {
      console.log('Received message:', data);
      addMessage(`Assistant: ${data.response}`);
    });

    webSocketService.onError((data) => {
      console.error('WebSocket error:', data);
      setError(data.message);
      addMessage(`Error: ${data.message}`);
    });

    webSocketService.onStatus((data) => {
      console.log('Status update:', data);
      addMessage(`Status: ${data.message}`);
    });

    return () => {
      webSocketService.disconnect();
    };
  }, []);

  const addMessage = (message: string) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const handleConnect = async () => {
    try {
      setConnectionState('connecting');
      setError(null);
      await webSocketService.connect();
      addMessage('System: Connection initiated');
    } catch (error) {
      console.error('Connection failed:', error);
      setError(`Connection failed: ${error}`);
      setConnectionState('disconnected');
      addMessage(`System: Connection failed - ${error}`);
    }
  };

  const handleDisconnect = () => {
    webSocketService.disconnect();
    setConnectionState('disconnected');
    addMessage('System: Manually disconnected');
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      addMessage(`You: ${inputMessage}`);
      await webSocketService.sendMessage(inputMessage);
      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
      setError(`Failed to send message: ${error}`);
      addMessage(`System: Failed to send message - ${error}`);
    }
  };

  const getConnectionColor = () => {
    switch (connectionState) {
      case 'connected': return '#4caf50';
      case 'connecting': return '#ff9800';
      case 'disconnected': return '#f44336';
      default: return '#757575';
    }
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '800px', margin: '0 auto' }}>
      <h2>WebSocket Test Component</h2>
      
      {/* Connection Status */}
      <div style={{ 
        padding: '1rem', 
        marginBottom: '1rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ 
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            backgroundColor: getConnectionColor(),
            color: 'white',
            fontWeight: 'bold'
          }}>
            {connectionState.toUpperCase()}
          </span>
          <span>Current Status: {webSocketService.getConnectionState()}</span>
        </div>
        
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            onClick={handleConnect}
            disabled={connectionState === 'connected' || connectionState === 'connecting'}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: connectionState === 'connected' ? '#ccc' : '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: connectionState === 'connected' ? 'not-allowed' : 'pointer'
            }}
          >
            Connect
          </button>
          <button 
            onClick={handleDisconnect}
            disabled={connectionState === 'disconnected'}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: connectionState === 'disconnected' ? '#ccc' : '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: connectionState === 'disconnected' ? 'not-allowed' : 'pointer'
            }}
          >
            Disconnect
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '1rem',
          marginBottom: '1rem',
          backgroundColor: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '4px',
          color: '#c62828'
        }}>
          <strong>Error:</strong> {error}
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

      {/* Message Input */}
      <div style={{ 
        display: 'flex', 
        gap: '0.5rem', 
        marginBottom: '1rem',
        padding: '1rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px'
      }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Enter a message to test WebSocket..."
          style={{
            flex: 1,
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
          disabled={connectionState !== 'connected'}
        />
        <button
          onClick={handleSendMessage}
          disabled={connectionState !== 'connected' || !inputMessage.trim()}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: connectionState !== 'connected' || !inputMessage.trim() ? '#ccc' : '#4caf50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: connectionState !== 'connected' || !inputMessage.trim() ? 'not-allowed' : 'pointer'
          }}
        >
          Send
        </button>
      </div>

      {/* Messages Log */}
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '4px',
        height: '300px',
        overflow: 'auto',
        padding: '1rem',
        backgroundColor: 'white'
      }}>
        <h3 style={{ margin: '0 0 1rem 0' }}>Message Log:</h3>
        {messages.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>No messages yet...</p>
        ) : (
          messages.map((message, index) => (
            <div key={index} style={{ 
              marginBottom: '0.5rem',
              padding: '0.25rem 0',
              borderBottom: '1px solid #eee',
              fontSize: '0.9rem'
            }}>
              {message}
            </div>
          ))
        )}
      </div>

      {/* Debug Info */}
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '4px',
        fontSize: '0.8rem',
        color: '#666'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0' }}>Debug Info:</h4>
        <p>WebSocket URL: {process.env.REACT_APP_WS_URL || 'http://localhost:5000'}</p>
        <p>Connection State: {webSocketService.getConnectionState()}</p>
        <p>Is Connected: {webSocketService.isConnected() ? 'Yes' : 'No'}</p>
      </div>
    </div>
  );
};

export default WebSocketTest;
