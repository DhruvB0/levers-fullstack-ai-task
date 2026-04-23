'use client';

import { marked } from 'marked';
import { useMemo } from 'react';

import type { Message } from '@/types';

marked.use({ breaks: true, gfm: true });

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user';
  const content = message.isStreaming ? message.content + '▍' : message.content;

  const html = useMemo(
    () => (isUser ? null : (marked.parse(content) as string)),
    [isUser, content],
  );

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-sm'
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <div
            className="md-content"
            dangerouslySetInnerHTML={{ __html: html ?? '' }}
          />
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {message.sources.map((source) => (
              <span
                key={source}
                className="rounded-full bg-gray-200 dark:bg-gray-700 px-2 py-0.5 text-xs text-gray-600 dark:text-gray-300"
              >
                {source}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
