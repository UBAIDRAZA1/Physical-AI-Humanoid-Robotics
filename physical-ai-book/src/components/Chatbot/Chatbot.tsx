import React, { useCallback, useEffect, useRef, useState } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './Chatbot.module.css';

type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  ts?: number;
};

type ChatbotProps = {
  apiBaseUrl?: string;
};

function getSelectionText(): string {
  if (typeof window === 'undefined') return '';
  const selection = window.getSelection();
  return selection ? selection.toString() : '';
}

const Chatbot: React.FC<ChatbotProps> = ({ apiBaseUrl }) => {
  const { siteConfig } = useDocusaurusContext();

  // Python backend URL use karo
  const backendBaseUrl = apiBaseUrl || 'https://hafizubaid-hackathon-my-backend-api.hf.space';
  const baseUrl = `${backendBaseUrl}/chat`;

  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [useSelectionOnly, setUseSelectionOnly] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  const refreshSelection = useCallback(() => {
    setSelectedText(getSelectionText());
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handler = () => refreshSelection();
    document.addEventListener('selectionchange', handler);
    return () => document.removeEventListener('selectionchange', handler);
  }, [refreshSelection]);

  useEffect(() => {
    if (!containerRef.current || typeof window === 'undefined') return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setIsVisible(true);
        });
      },
      { threshold: 0.1 }
    );
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const renderMessageContent = (content: string) => {
    const fence = '```';
    if (content.includes(fence)) {
      const parts = content.split(fence);
      const pre = parts[1]?.trim() || '';
      const before = parts[0]?.trim();
      const after = parts[2]?.trim();
      return (
        <>
          {before && <div className={styles.messageParagraph}>{before}</div>}
          {pre && (
            <pre className={styles.codeBlock}>
              <code>{pre}</code>
            </pre>
          )}
          {after && <div className={styles.messageParagraph}>{after}</div>}
        </>
      );
    }
    return <div className={styles.messageContent}>{content}</div>;
  };

  const sendQuestion = async () => {
    const trimmed = question.trim();
    if (!trimmed) return;

    const currentSelection = getSelectionText();
    
    // If checkbox is checked, require selected text
    if (useSelectionOnly && !currentSelection.trim()) {
      const errorMsg: ChatMessage = {
        id: `${Date.now()}-error`,
        role: 'assistant',
        content: 'Please select some text first when using "Answer only from selected text" mode.',
      };
      setMessages(prev => [...prev, errorMsg]);
      return;
    }
    
    // If checkbox is checked, use selected text only
    // If checkbox is not checked, send selected text as additional context if available
    const selectionToSend = useSelectionOnly 
      ? currentSelection.trim()  // Always send when checkbox is checked (we validated it's not empty above)
      : (currentSelection.trim() || undefined);  // Send undefined if checkbox not checked and no selection

    console.log('Sending question:', {
      question: trimmed,
      useSelectionOnly,
      hasSelection: currentSelection.trim().length > 0,
      selectionLength: currentSelection.trim().length,
      selectionToSend: selectionToSend ? `${selectionToSend.substring(0, 50)}...` : 'none',
    });

    const userMsg: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: trimmed,
      ts: Date.now(),
    };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setIsLoading(true);

    try {
      // Add timeout to prevent hanging (60 seconds for Gemini API)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      const requestBody = {
        question: trimmed,
        selected_text: selectionToSend || undefined,
        conversation_id: conversationId,
        use_selection_only: useSelectionOnly,
      };

      console.log('API Request:', {
        url: baseUrl,
        body: { ...requestBody, selected_text: requestBody.selected_text ? `${requestBody.selected_text.substring(0, 50)}...` : undefined },
      });

      const res = await fetch(baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        let errorText = '';
        try {
          const errorData = await res.json();
          errorText = errorData.detail || errorData.message || errorData.error || `HTTP ${res.status}`;
        } catch {
          errorText = await res.text() || `HTTP ${res.status}`;
        }
        console.error('API Error:', res.status, errorText);
        throw new Error(errorText);
      }

      const data: { answer: string; conversation_id: string } = await res.json();
      console.log('API Response:', {
        hasAnswer: !!data.answer,
        answerLength: data.answer?.length || 0,
        conversationId: data.conversation_id,
      });

      if (!data.answer) {
        throw new Error('Empty response from server');
      }

      setConversationId(data.conversation_id);

      const assistantMsg: ChatMessage = {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: data.answer,
        ts: Date.now(),
      };
      setMessages(prev => [...prev, assistantMsg]);

    } catch (error: any) {
      console.error('Chat error:', error);
      let errorMessage = 'Unable to get response from server.';
      
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out. The server is taking too long to respond.';
      } else if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
        errorMessage = 'Cannot connect to backend server. Is the backend running? (http://localhost:8000)';
      } else if (error.message?.includes('404')) {
        errorMessage = 'API endpoint not found. Please check the backend.';
      } else if (error.message?.includes('500')) {
        errorMessage = 'Server error occurred. Please check backend logs.';
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      
      const assistantMsg: ChatMessage = {
        id: `${Date.now()}-error`,
        role: 'assistant',
        content: errorMessage,
        ts: Date.now(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void sendQuestion();
    }
  };

  const hasSelection = selectedText.trim().length > 0;

  return (
    <div id="chat" ref={containerRef} className={`${styles.chatbotContainer} ${isVisible ? styles.visible : ''}`}>
      <div className={styles.header}>
        <h2 className={styles.title}>Book Assistant</h2>
        <p className={styles.subtitle}>
          Ask questions, select text — get instant answers!
        </p>
      </div>

      <div className={styles.selectionBar}>
        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={useSelectionOnly}
            onChange={(e) => setUseSelectionOnly(e.target.checked)}
            disabled={!hasSelection}
          />
          <span>Answer only from selected text</span>
        </label>
        <button type="button" className={styles.selectionButton} onClick={refreshSelection}>
          Refresh Selection
        </button>
      </div>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            Get started, for example:
            <br />
            <code>What is forward kinematics?</code>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={msg.role === 'user' ? styles.messageUser : styles.messageAssistant}>
            <div className={styles.messageHeader}>
              <div className={styles.avatar}>{msg.role === 'user' ? 'Y' : 'A'}</div>
              <div className={styles.meta}>
                <span className={styles.messageRole}>{msg.role === 'user' ? 'You' : 'Assistant'}</span>
                <span className={styles.dot}>•</span>
                <span className={styles.timestamp}>
                  {msg.ts ? new Date(msg.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
              </div>
            </div>
            <div className={styles.bubble}>
              {renderMessageContent(msg.content)}
            </div>
          </div>
        ))}
        {isLoading && <div className={styles.typingIndicator}>Assistant is thinking…</div>}
      </div>

      <div className={styles.inputBar}>
        <textarea
          className={styles.textarea}
          placeholder="Type your question here…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
        />
        <button
          type="button"
          className={styles.sendButton}
          onClick={sendQuestion}
          disabled={isLoading || question.trim().length === 0}
        >
          {isLoading ? 'Sending…' : 'Ask'}
        </button>
      </div>
      <div className={styles.suggestions}>
        <button type="button" className={styles.suggestChip} onClick={() => setQuestion('Explain inverse kinematics with example')}>
          Explain inverse kinematics with example
        </button>
        <button type="button" className={styles.suggestChip} onClick={() => setQuestion('Summarize the selected paragraph')}>
          Summarize the selected paragraph
        </button>
        <button type="button" className={styles.suggestChip} onClick={() => setQuestion('How does ROS 2 handle topics?')}>
          How does ROS 2 handle topics?
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
