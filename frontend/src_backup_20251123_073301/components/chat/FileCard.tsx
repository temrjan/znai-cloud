/**
 * File Card component
 * Shows file/document preview in chat
 */
import { Box } from '../common/Box';
import { FileIcon, ChevronRightIcon } from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';

interface FileCardProps {
  filename: string;
  preview?: string;
  onClick?: () => void;
}

export function FileCard({ filename, preview, onClick }: FileCardProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];

  return (
    <Box
      as="button"
      onClick={onClick}
      sx={{
        width: '100%',
        backgroundColor: themeColors.bg.secondary,
        border: `1px solid ${themeColors.border.primary}`,
        borderRadius: '8px',
        padding: '12px',
        marginTop: '12px',
        cursor: onClick ? 'pointer' : 'default',
        textAlign: 'left',
        transition: 'all 0.2s ease',
        '&:hover': onClick
          ? {
              backgroundColor: themeColors.bg.tertiary,
              borderColor: themeColors.border.secondary,
            }
          : {},
      }}
    >
      {/* Header: Icon + Filename + Expand */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: preview ? '8px' : 0,
        }}
      >
        <FileIcon size={20} fill={themeColors.text.secondary} />
        <Box
          sx={{
            flex: 1,
            fontSize: '14px',
            fontWeight: 600,
            color: themeColors.text.primary,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {filename}
        </Box>
        {onClick && <ChevronRightIcon size={16} fill={themeColors.text.tertiary} />}
      </Box>

      {/* Preview content */}
      {preview && (
        <Box
          sx={{
            fontSize: '13px',
            color: themeColors.text.secondary,
            lineHeight: 1.5,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {preview}
        </Box>
      )}
    </Box>
  );
}
