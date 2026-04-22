import { act, renderHook } from '@testing-library/react';

import { useChat } from '@/hooks/useChat';
import * as api from '@/lib/api';

jest.mock('@/lib/api');

const mockSendChatMessage = api.sendChatMessage as jest.MockedFunction<typeof api.sendChatMessage>;

describe('useChat', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with empty messages', () => {
    const { result } = renderHook(() => useChat());
    expect(result.current.messages).toHaveLength(0);
  });

  it('adds user message immediately on send', async () => {
    mockSendChatMessage.mockResolvedValue({
      answer: 'Test answer',
      sources: [],
      rag_used: true,
    });
    const { result } = renderHook(() => useChat());

    await act(async () => {
      result.current.setStreamingEnabled(false);
    });

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.messages[0]).toMatchObject({ role: 'user', content: 'Hello' });
  });

  it('adds assistant response after non-streaming send', async () => {
    mockSendChatMessage.mockResolvedValue({
      answer: 'Test answer',
      sources: ['fdcpa.md'],
      rag_used: true,
    });
    const { result } = renderHook(() => useChat());

    await act(async () => {
      result.current.setStreamingEnabled(false);
    });

    await act(async () => {
      await result.current.sendMessage('What are calling hours?');
    });

    const assistant = result.current.messages.find((m) => m.role === 'assistant');
    expect(assistant?.content).toBe('Test answer');
    expect(assistant?.sources).toEqual(['fdcpa.md']);
  });

  it('does not send empty or whitespace-only messages', async () => {
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage('   ');
    });
    expect(result.current.messages).toHaveLength(0);
    expect(mockSendChatMessage).not.toHaveBeenCalled();
  });

  it('handles API errors gracefully', async () => {
    mockSendChatMessage.mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useChat());

    await act(async () => {
      result.current.setStreamingEnabled(false);
    });

    await act(async () => {
      await result.current.sendMessage('Test query');
    });

    const assistant = result.current.messages.find((m) => m.role === 'assistant');
    expect(assistant?.content).toBe('Something went wrong. Please try again.');
  });

  it('updates model selection', () => {
    const { result } = renderHook(() => useChat());
    act(() => {
      result.current.setModel('o1-mini');
    });
    expect(result.current.model).toBe('o1-mini');
  });
});
