'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

import { sendChatMessage, streamChatMessage } from '@/lib/api';
import { THINKING_MODELS } from '@/lib/constants';
import type { Message, Model } from '@/types';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [model, _setModel] = useState<Model>('gpt-4o-mini');
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  const abortRef = useRef<AbortController | null>(null);

  const setModel = useCallback((next: Model) => {
    _setModel(next);
    if (THINKING_MODELS.has(next)) setStreamingEnabled(false);
  }, []);

  useEffect(() => {
    return () => { abortRef.current?.abort(); };
  }, []);

  const addMessage = useCallback(
    (role: Message['role'], content: string, sources?: string[]) => {
      const id = uuidv4();
      setMessages((prev) => [...prev, { id, role, content, sources }]);
      return id;
    },
    [],
  );

  const sendMessage = useCallback(
    async (query: string) => {
      if (!query.trim() || isLoading) return;

      addMessage('user', query);
      setIsLoading(true);

      try {
        if (streamingEnabled) {
          abortRef.current?.abort();
          const controller = new AbortController();
          abortRef.current = controller;

          const assistantId = uuidv4();
          setMessages((prev) => [
            ...prev,
            { id: assistantId, role: 'assistant', content: '', isStreaming: true },
          ]);

          await streamChatMessage(
            { query, model, stream: true },
            (token) => {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantId
                    ? { ...msg, content: msg.content + token }
                    : msg,
                ),
              );
            },
            () => {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantId ? { ...msg, isStreaming: false } : msg,
                ),
              );
              setIsLoading(false);
            },
            controller.signal,
          );
        } else {
          const response = await sendChatMessage({ query, model, stream: false });
          addMessage('assistant', response.answer, response.sources);
          setIsLoading(false);
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') return;
        addMessage('assistant', 'Something went wrong. Please try again.');
        setIsLoading(false);
      }
    },
    [isLoading, model, streamingEnabled, addMessage],
  );

  return {
    messages,
    isLoading,
    model,
    streamingEnabled,
    setModel,
    setStreamingEnabled,
    sendMessage,
  };
}
