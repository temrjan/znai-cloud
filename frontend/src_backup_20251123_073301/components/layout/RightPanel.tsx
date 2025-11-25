/**
 * Right Panel - Document viewer
 * Width: 400px, appears when document is opened
 */
import { Box } from '../common/Box';
import { XIcon } from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';

interface RightPanelProps {
  isOpen: boolean;
  onClose: () => void;
  filename?: string;
  content?: string;
}

export function RightPanel({ isOpen, onClose, filename, content }: RightPanelProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];

  if (!isOpen) return null;

  return (
    <Box
      sx={{
        width: '400px',
        height: '100vh',
        backgroundColor: themeColors.bg.primary,
        borderLeft: `1px solid ${themeColors.border.primary}`,
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        right: 0,
        top: 0,
        zIndex: 40,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          padding: '16px',
          borderBottom: `1px solid ${themeColors.border.primary}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Box
          sx={{
            fontSize: '14px',
            fontWeight: 600,
            color: themeColors.text.primary,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            flex: 1,
          }}
        >
          {filename || 'Document'}
        </Box>
        <Box
          as="button"
          onClick={onClose}
          aria-label="Close"
          sx={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            color: themeColors.text.secondary,
          }}
        >
          <XIcon size={16} />
        </Box>
      </Box>

      {/* Content */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          paddingBottom: '120px',
        }}
      >
        <Box
          sx={{
            backgroundColor: themeColors.bg.secondary,
            border: `1px solid ${themeColors.border.primary}`,
            borderRadius: '8px',
            padding: '16px',
            fontSize: '14px',
            lineHeight: 1.6,
            color: themeColors.text.primary,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {content || 'No content available'}
        </Box>
      </Box>
    </Box>
  );
}
