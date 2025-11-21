/**
 * Message Actions component
 * Buttons: like, dislike, copy, refresh
 */
import { Box } from '../common/Box';
import { ThumbsupIcon, ThumbsdownIcon, CopyIcon, SyncIcon } from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';

interface MessageActionsProps {
  onLike?: () => void;
  onDislike?: () => void;
  onCopy?: () => void;
  onRefresh?: () => void;
}

export function MessageActions({ onLike, onDislike, onCopy, onRefresh }: MessageActionsProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];

  const buttonStyle = {
    width: '32px',
    height: '32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    color: themeColors.text.tertiary,
  };

  return (
    <Box
      sx={{
        display: 'flex',
        gap: '8px',
        marginTop: '8px',
      }}
    >
      <Box
        as="button"
        onClick={onLike}
        aria-label="Like"
        sx={buttonStyle}
      >
        <ThumbsupIcon size={16} />
      </Box>
      <Box
        as="button"
        onClick={onDislike}
        aria-label="Dislike"
        sx={buttonStyle}
      >
        <ThumbsdownIcon size={16} />
      </Box>
      <Box
        as="button"
        onClick={onCopy}
        aria-label="Copy"
        sx={buttonStyle}
      >
        <CopyIcon size={16} />
      </Box>
      <Box
        as="button"
        onClick={onRefresh}
        aria-label="Refresh"
        sx={buttonStyle}
      >
        <SyncIcon size={16} />
      </Box>
    </Box>
  );
}
