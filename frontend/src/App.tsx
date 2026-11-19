import React, { useState, useEffect, useRef, useCallback } from 'react';
import ModelSelector from './components/models/ModelSelector';
import { StatusBadge } from './design-system/patterns/StatusBadge/StatusBadge';
import { getConfig, getHealth } from './platform/api/client';
import { fmt } from './platform/format/format';
import { t } from './platform/i18n/t';
import { reduceAssistantMessage } from './platform/stream/legacyChatAdapter';
import { openChatStream } from './platform/stream/openChatStream';
import { getUUID } from './utils/uuid';

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

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | undefined>(undefined);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // Add welcome message
    addMessage('system', t('app.welcome'));
    loadConfig();
    checkConnection();
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
      await getHealth();
      setIsConnected(true);
      addMessage('system', t('app.connected'));
    } catch (error) {
      setIsConnected(false);
      addMessage('system', t('app.backendDown'));
    }
  }, []);

  const loadConfig = async () => {
    try {
      const config = await getConfig();
      console.log('Backend configuration loaded:', config);
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

    const handle = openChatStream(
      {
        message: userMessage,
        stream: true,
        ...(selectedProvider ? { provider: selectedProvider } : {}),
      },
      { signal: controller.signal },
    );
    try {
      for await (const event of handle.events) {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? reduceAssistantMessage(m, event) : m)),
        );
      }
      if (handle.outcome() === 'aborted') {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false, content: m.content + '\n' + t('app.cancelled') } : m)),
        );
      } else if (handle.outcome() === 'interrupted') {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false } : m)),
        );
      }
    } catch (e: any) {
      if (e.name === 'AbortError') {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false, content: m.content + '\n' + t('app.cancelled') } : m))
        );
      } else {
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false, content: `${t('app.errorPrefix')}: ${e.message}` } : m))
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

  const getMessageStyle = (type: string) => {
    const base: React.CSSProperties = {
      padding: '8px 12px',
      borderRadius: 6,
      marginBottom: 8,
      maxWidth: '80%',
      whiteSpace: 'pre-wrap',
      lineHeight: 1.4,
      border: '1px solid var(--surface-line)',
      color: 'var(--surface-text)',
      fontSize: 14,
      position: 'relative'
    };
    if (type === 'user') {
      base.background = 'var(--surface-card)';
      base.alignSelf = 'flex-end';
    } else if (type === 'assistant') {
      base.background = 'var(--surface-bg)';
    } else {
      base.background = 'var(--surface-card)';
    }
    return base;
  };

  const handleModelChange = (provider: string, modelName: string) => {
    console.log(`Model changed to: ${provider}/${modelName}`);
    // The selection is already updated on the backend
  };

  return (
    <div data-ui="shell" style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--surface-bg)', color: 'var(--surface-text)' }}>
      <header style={{ padding: '8px 12px', borderBottom: '1px solid var(--surface-line)', display: 'flex', gap: 12, alignItems: 'center' }}>
        <h1 style={{ fontSize: 16, margin: 0 }}>{t('app.title')}</h1>
        <ModelSelector compact onModelChange={handleModelChange} disabled={isLoading} />
        <select
          value={selectedProvider || ''}
          onChange={e => setSelectedProvider(e.target.value || undefined)}
          style={{ padding: '4px 8px', background: 'var(--surface-card)', color: 'var(--surface-text)', border: '1px solid var(--surface-line)' }}
          title={t('app.modelOverride')}
        >
          <option value="">{t('app.provider.auto')}</option>
          <option value="openai">{t('app.provider.openai')}</option>
          <option value="grok">{t('app.provider.grok')}</option>
        </select>
        <button
          onClick={sendMessage}
          disabled={isLoading}
          style={{ padding: '4px 12px' }}
        >
          {isLoading ? t('app.sending') : t('app.send')}
        </button>
        <button
          onClick={cancelStreaming}
          disabled={!isLoading || !abortRef.current}
          style={{ padding: '4px 12px' }}
        >
          {t('app.cancel')}
        </button>
        <div style={{ marginLeft: 'auto', fontSize: 12 }}>
          {isLoading ? t('app.streaming') : isConnected ? t('app.online') : t('app.offline')}
        </div>
      </header>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column' }}>
        {messages.map(m => (
          <div
            key={m.id}
            style={getMessageStyle(m.type)}
          >
            <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>
              {m.type === 'user' ? t('app.role.user') : m.type === 'assistant' ? t('app.role.assistant') : t('app.role.system')}
              {' '}
              <time data-fmt="date" dateTime={m.timestamp}>{fmt.dateTime(m.timestamp)}</time>
              {m.provider ? ` · ${m.provider}${m.model ? ':' + m.model : ''}` : ''} {m.fallback ? <> · <StatusBadge status="warn" label={t('app.fallback')} /></> : null}
              {m.isStreaming && ` · ${t('app.streamingFlag')}`}
            </div>
            {m.content || <em style={{ opacity: 0.6 }}>{t('app.pending')}</em>}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ borderTop: '1px solid var(--surface-line)', padding: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {error && <StatusBadge status="danger" label={error} />}
        <textarea
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder={t('app.placeholder')}
          style={{ width: '100%', height: 70, resize: 'vertical', padding: 8, background: 'var(--surface-card)', color: 'var(--surface-text)', border: '1px solid var(--surface-line)' }}
        />
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={sendMessage} disabled={isLoading} style={{ padding: '6px 14px' }}>
            {t('app.send')}
          </button>
          <button onClick={cancelStreaming} disabled={!isLoading || !abortRef.current} style={{ padding: '6px 14px' }}>
            {t('app.cancel')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
