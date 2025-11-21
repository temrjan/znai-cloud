/**
 * Chat Message component
 * Supports user and assistant messages
 */
import { Box } from '../common/Box';
import { CommentDiscussionIcon } from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';
import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const isUser = message.role === 'user';

  if (isUser) {
    // User message - aligned right with border
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          marginBottom: '16px',
        }}
      >
        <Box
          sx={{
            maxWidth: '85%',
            padding: '12px 16px',
            border: `1px solid ${themeColors.border.primary}`,
            borderRadius: '8px',
            backgroundColor: themeColors.bg.secondary,
          }}
        >
          <Box
            sx={{
              fontSize: '16px',
              lineHeight: 1.5,
              color: themeColors.text.primary,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {message.content}
          </Box>
          <Box
            sx={{
              marginTop: '4px',
              fontSize: '12px',
              color: themeColors.text.tertiary,
              textAlign: 'right',
            }}
          >
            {new Date(message.timestamp).toLocaleTimeString('ru-RU', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Box>
        </Box>
      </Box>
    );
  }

  // Assistant message - aligned left without border
  return (
    <Box
      sx={{
        display: 'flex',
        gap: '12px',
        marginBottom: '16px',
        alignItems: 'flex-start',
      }}
    >
      {/* Icon */}
      <Box
        sx={{
          width: '32px',
          height: '32px',
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: themeColors.text.secondary,
        }}
      >
        <CommentDiscussionIcon size={24} />
      </Box>

      {/* Message content */}
      <Box
        sx={{
          flex: 1,
          minWidth: 0,
        }}
      >
        <Box
          sx={{
            fontSize: '16px',
            lineHeight: 1.5,
            color: themeColors.text.primary,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {message.content}
        </Box>

        {/* Sources if available */}
        {message.sources && message.sources.length > 0 && (
          <Box
            sx={{
              marginTop: '8px',
              fontSize: '12px',
              color: themeColors.text.secondary,
              fontStyle: 'italic',
            }}
          >
            Sources: {message.sources.join(', ')}
          </Box>
        )}

        {/* Timestamp */}
        <Box
          sx={{
            marginTop: '4px',
            fontSize: '12px',
            color: themeColors.text.tertiary,
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Box>
      </Box>
    </Box>
  );
}

// Loading message component
interface LoadingMessageProps {
  text?: string;
}

export function LoadingMessage({ text = 'Copilot is responding...' }: LoadingMessageProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];

  return (
    <Box
      sx={{
        display: 'flex',
        gap: '12px',
        marginBottom: '16px',
        alignItems: 'center',
      }}
    >
      {/* Icon */}
      <Box
        sx={{
          width: '32px',
          height: '32px',
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: themeColors.text.secondary,
        }}
      >
        <CommentDiscussionIcon size={24} />
      </Box>

      {/* Loading text */}
      <Box
        sx={{
          fontSize: '14px',
          color: themeColors.text.secondary,
          fontStyle: 'italic',
        }}
      >
        {text}
      </Box>
    </Box>
  );
}
