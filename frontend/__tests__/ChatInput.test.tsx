import { fireEvent, render, screen } from '@testing-library/react';

import ChatInput from '@/components/ChatInput';

describe('ChatInput', () => {
  it('calls onSend with trimmed input when Enter is pressed', () => {
    const mockSend = jest.fn();
    render(<ChatInput onSend={mockSend} isLoading={false} />);

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'What are calling hours?' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    expect(mockSend).toHaveBeenCalledWith('What are calling hours?');
  });

  it('does not submit on Shift+Enter', () => {
    const mockSend = jest.fn();
    render(<ChatInput onSend={mockSend} isLoading={false} />);

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'test' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    expect(mockSend).not.toHaveBeenCalled();
  });

  it('disables the send button while loading', () => {
    render(<ChatInput onSend={jest.fn()} isLoading={true} />);
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled();
  });

  it('disables the send button when input is empty', () => {
    render(<ChatInput onSend={jest.fn()} isLoading={false} />);
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled();
  });

  it('enables the send button when input has text and not loading', () => {
    render(<ChatInput onSend={jest.fn()} isLoading={false} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'hello' } });
    expect(screen.getByRole('button', { name: /send/i })).not.toBeDisabled();
  });

  it('clears input after sending', () => {
    render(<ChatInput onSend={jest.fn()} isLoading={false} />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'test message' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });
    expect(textarea).toHaveValue('');
  });
});
