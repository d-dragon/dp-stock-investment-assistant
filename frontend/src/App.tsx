import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';
import WebSocketTest from './components/WebSocketTest';
import { restApiClient } from './services/restApiClient';

// Interface definitions
interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  provider?: string;
  model?: string;
  fallback?: boolean;
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
  const [selectedProvider, setSelectedProvider] = useState<string | undefined>(undefined);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  
  const API_BASE_URL = 'http://localhost:5000';

  useEffect(() => {
    // Add welcome message
    addMessage('system', 'Welcome to DP Stock Investment Assistant! Please start the backend server first.');
    loadConfig();
    checkConnection();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (type: 'user' | 'assistant' | 'system', content: string, timestamp?: string, extra?: Partial<Message>) => {
    const newMessage: Message = {
      id: getUUID(),
      type,
      content,
      timestamp: timestamp || new Date().toISOString(),
      isStreaming: false,
      ...extra
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const checkConnection = useCallback(async () => {
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
  }, []);

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
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    const userMessage = inputValue.trim();
    setInputValue('');
    addMessage('user', userMessage);
    setIsLoading(true);
    setError(null);

    // Create streaming placeholder
    const assistantId = getUUID();
    setMessages(prev => [
      ...prev,
      {
        id: assistantId,
        type: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        isStreaming: true
      }
    ]);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await restApiClient.streamChat(
        userMessage,
        (chunk: string | { event: string; provider?: string; model?: string; fallback?: boolean; error?: string } | null) => {
          setMessages(prev =>
            prev.map(m => {
              if (m.id !== assistantId) return m;
              // Meta / done events
              if (typeof chunk === 'object' && chunk !== null) {
                if (chunk.event === 'meta') {
                  return { ...m, provider: chunk.provider, model: chunk.model };
                }
                if (chunk.event === 'done') {
                  return {
                    ...m,
                    isStreaming: false,
                    fallback: !!chunk.fallback,
                    provider: chunk.provider || m.provider,
                    model: chunk.model || m.model
                  };
                }
                if (chunk.event === 'error') {
                  return { ...m, isStreaming: false, content: (m.content || '') + `\n[Error] ${chunk.error}` };
                }
              } else if (typeof chunk === 'string') {
                return { ...m, content: m.content + chunk };
              }
              return m;
            })
          );
        },
        { provider: selectedProvider, signal: controller.signal }
      );
    } catch (e: any) {
      if (e.name === 'AbortError') {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false, content: m.content + '\n[Cancelled]' } : m))
        );
      } else {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false, content: `[Error] ${e.message}` } : m))
        );
        setError(e.message);
      }
    } finally {
      abortRef.current = null;
      setIsLoading(false);
    }
  };

  const cancelStreaming = () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getMessageStyle = (type: string, fallback?: boolean) => {
    const base: React.CSSProperties = {
      padding: '8px 12px',
      borderRadius: 6,
      marginBottom: 8,
      maxWidth: '80%',
      whiteSpace: 'pre-wrap',
      lineHeight: 1.4,
      border: '1px solid #e0e0e0',
      fontFamily: 'system-ui, Arial, sans-serif',
      fontSize: 14,
      position: 'relative'
    };
    if (type === 'user') {
      base.background = '#e6f2ff';
      base.alignSelf = 'flex-end';
    } else if (type === 'assistant') {
      base.background = '#fafafa';
    } else {
      base.background = '#fff8e1';
    }
    if (fallback) {
      base.borderLeft = '4px solid #ff9800';
      base.paddingLeft = 8;
    }
    return base;
  };

  return (
    <div style={{ fontFamily: 'system-ui, Arial, sans-serif', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header / Controls */}
      <div style={{ padding: '8px 12px', borderBottom: '1px solid #ddd', display: 'flex', gap: 12, alignItems: 'center' }}>
        <strong>DP Stock Investment Assistant</strong>
        <select
          value={selectedProvider || ''}
          onChange={e => setSelectedProvider(e.target.value || undefined)}
          style={{ padding: '4px 8px' }}
          title="Select model provider"
        >
          <option value="">Auto (config)</option>
          <option value="openai">OpenAI</option>
          <option value="grok">Grok (stub)</option>
        </select>
        <button
          onClick={sendMessage}
          disabled={isLoading}
          style={{ padding: '4px 12px' }}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
        <button
          onClick={cancelStreaming}
          disabled={!isLoading || !abortRef.current}
          style={{ padding: '4px 12px' }}
        >
          Cancel
        </button>
        <div style={{ marginLeft: 'auto', fontSize: 12 }}>
          {isLoading ? 'Streaming...' : isConnected ? 'Online' : 'Offline'}
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column' }}>
        {messages.map(m => (
          <div
            key={m.id}
            style={getMessageStyle(m.type, m.fallback)}
          >
            <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>
              {m.type.toUpperCase()} {m.provider ? `· ${m.provider}${m.model ? ':' + m.model : ''}` : ''} {m.fallback ? '· fallback' : ''}
              {m.isStreaming && ' · streaming'}
            </div>
            {m.content || <em style={{ opacity: 0.6 }}>...</em>}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ borderTop: '1px solid #ddd', padding: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {error && <div style={{ color: 'red', fontSize: 12 }}>{error}</div>}
        <textarea
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask about stocks, e.g. 'Latest news on AAPL and MSFT'"
          style={{ width: '100%', height: 70, resize: 'vertical', padding: 8, fontFamily: 'inherit' }}
        />
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={sendMessage} disabled={isLoading} style={{ padding: '6px 14px' }}>
            Send
          </button>
          <button onClick={cancelStreaming} disabled={!isLoading || !abortRef.current} style={{ padding: '6px 14px' }}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
