import React, { useCallback, useEffect, useState } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './Chatbot.module.css';

type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
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
  const backendBaseUrl = apiBaseUrl || (siteConfig.customFields?.apiBaseUrl as string) || 'http://localhost:8000';
  const baseUrl = `${backendBaseUrl}/chat`;

  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [useSelectionOnly, setUseSelectionOnly] = useState(false);

  const refreshSelection = useCallback(() => {
    setSelectedText(getSelectionText());
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handler = () => refreshSelection();
    document.addEventListener('selectionchange', handler);
    return () => document.removeEventListener('selectionchange', handler);
  }, [refreshSelection]);

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
    <div className={styles.chatbotContainer}>
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
          <div
            key={msg.id}
            className={msg.role === 'user' ? styles.messageUser : styles.messageAssistant}
          >
            <div className={styles.messageRole}>
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div className={styles.messageContent}>{msg.content}</div>
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
    </div>
  );
};

export default Chatbot;