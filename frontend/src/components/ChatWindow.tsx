'use client';

import { useChat } from '@/hooks/useChat';
import ChatInput from './ChatInput';
import ControlBar from './ControlBar';
import FileUpload from './FileUpload';
import MessageList from './MessageList';
import StatusBadge from './StatusBadge';

export default function ChatWindow() {
  const { messages, isLoading, model, streamingEnabled, setModel, setStreamingEnabled, sendMessage } =
    useChat();

  return (
    <div className="flex h-screen flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3">
        <div>
          <h1 className="text-sm font-semibold text-gray-900">Debt Collection Assistant</h1>
          <p className="text-xs text-gray-500">Compliance copilot — powered by RAG</p>
        </div>
        <StatusBadge />
      </div>

      {/* Model + streaming controls */}
      <ControlBar
        model={model}
        setModel={setModel}
        streamingEnabled={streamingEnabled}
        setStreamingEnabled={setStreamingEnabled}
      />

      {/* Message thread */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Document upload */}
      <FileUpload />

      {/* Chat input */}
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}
