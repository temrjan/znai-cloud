/**
 * Chat Input component - Footer with input field
 * Fixed at bottom, expandable textarea
 */
import { useState, useRef, useEffect } from 'react';
import { Box } from '../common/Box';
import { TriangleRightIcon, StopIcon } from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';

interface ChatInputProps {
  onSend: (message: string) => void;
  loading?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  loading = false,
  disabled = false,
  placeholder = 'Ask anything',
}: ChatInputProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading || disabled) return;

    onSend(input);
    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Box
      as="form"
      onSubmit={handleSubmit}
      sx={{
        width: '100%',
        maxWidth: '900px',
        margin: '0 auto',
        padding: '0 24px',
      }}
    >
      {/* Textarea with button inside */}
      <Box
        sx={{
          position: 'relative',
          width: '100%',
        }}
      >
        <style>{`
          .chat-textarea {
            width: 100%;
            min-height: 80px;
            max-height: 300px;
            background-color: ${themeColors.bg.secondary};
            border: 2px solid ${themeColors.border.primary};
            border-radius: 12px;
            padding: 16px 70px 16px 16px;
            font-size: 16px;
            line-height: 1.5;
            color: ${themeColors.text.primary};
            resize: none;
            font-family: inherit;
            outline: none;
            transition: all 0.2s ease;
          }
          .chat-textarea:hover {
            border-color: ${themeColors.accent.blueHover};
          }
          .chat-textarea:focus {
            border-color: ${themeColors.accent.blueHover};
            box-shadow: 0 0 0 3px ${themeColors.accent.blueHover}22;
          }
          .chat-textarea:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }
          .chat-textarea::placeholder {
            color: ${themeColors.text.tertiary};
          }
        `}</style>
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          value={input}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={loading ? 'znai больше...' : placeholder}
          disabled={loading || disabled}
        />

        {/* Send/Stop button - positioned inside textarea */}
        <Box
          as="button"
          type="submit"
          disabled={(!input.trim() && !loading) || disabled}
          sx={{
            position: 'absolute',
            bottom: '12px',
            right: '12px',
            width: '44px',
            height: '44px',
            padding: 0,
            background: loading
              ? themeColors.accent.red
              : themeColors.accent.blueGradient,
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: (!input.trim() && !loading) || disabled ? 'not-allowed' : 'pointer',
            opacity: (!input.trim() && !loading) || disabled ? 0.5 : 1,
            transition: 'all 0.2s ease',
            '&:hover': (!input.trim() && !loading) || disabled ? {} : {
              opacity: loading ? 1 : 0.9,
            },
          }}
          aria-label={loading ? 'Stop' : 'Send'}
        >
          {loading ? <StopIcon size={16} /> : <TriangleRightIcon size={16} />}
        </Box>
      </Box>
    </Box>
  );
}
