import React, {useCallback, useEffect, useState} from 'react';
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

const Chatbot: React.FC<ChatbotProps> = ({apiBaseUrl}) => {
  const {siteConfig} = useDocusaurusContext();
  const defaultApiBase = (siteConfig.customFields?.apiBaseUrl as string) || 'http://localhost:8000';

  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [useSelectionOnly, setUseSelectionOnly] = useState(false);
  const baseUrl = apiBaseUrl || defaultApiBase;

  const refreshSelection = useCallback(() => {
    setSelectedText(getSelectionText());
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handler = () => {
      refreshSelection();
    };
    document.addEventListener('selectionchange', handler);
    return () => document.removeEventListener('selectionchange', handler);
  }, [refreshSelection]);

  const sendQuestion = async () => {
    const trimmed = question.trim();
    if (!trimmed) return;

    const currentSelection = getSelectionText();
    const selectionToSend =
      useSelectionOnly && currentSelection.trim().length > 0 ? currentSelection : undefined;

    const userMsg: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: trimmed,
    };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setIsLoading(true);

    try {
      const res = await fetch(`${baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: trimmed,
          selected_text: selectionToSend,
          conversation_id: conversationId,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: {answer: string; conversation_id: string} = await res.json();
      setConversationId(data.conversation_id);

      const assistantMsg: ChatMessage = {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: data.answer,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch {
      const assistantMsg: ChatMessage = {
        id: `${Date.now()}-assistant-error`,
        role: 'assistant',
        content:
          'Sorry, something went wrong talking to the backend. Please make sure the FastAPI server is running.',
      };
      setMessages(prev => [...prev, assistantMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = e => {
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
          Ask questions about this book. Optionally select text first to limit the answer to just
          that selection.
        </p>
      </div>

      <div className={styles.selectionBar}>
        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={useSelectionOnly}
            onChange={e => setUseSelectionOnly(e.target.checked)}
            disabled={!hasSelection}
          />
          <span>Answer using only my selected text</span>
        </label>
        <button type="button" className={styles.selectionButton} onClick={refreshSelection}>
          Refresh selection
        </button>
        <span className={styles.selectionStatus}>
          {hasSelection
            ? 'Selection captured from page.'
            : 'Select some text in the page to enable selection-only answers.'}
        </span>
      </div>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            Start by asking a question about the book, for example:
            <br />
            <code>What is the main idea of this chapter?</code>
          </div>
        )}
        {messages.map(msg => (
          <div
            key={msg.id}
            className={msg.role === 'user' ? styles.messageUser : styles.messageAssistant}>
            <div className={styles.messageRole}>{msg.role === 'user' ? 'You' : 'Assistant'}</div>
            <div className={styles.messageContent}>{msg.content}</div>
          </div>
        ))}
        {isLoading && <div className={styles.typingIndicator}>Assistant is thinking…</div>}
      </div>

      <div className={styles.inputBar}>
        <textarea
          className={styles.textarea}
          placeholder="Ask a question about the book…"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
        />
        <button
          type="button"
          className={styles.sendButton}
          onClick={sendQuestion}
          disabled={isLoading || question.trim().length === 0}>
          {isLoading ? 'Sending…' : 'Ask'}
        </button>
      </div>
    </div>
  );
};

export default Chatbot;

