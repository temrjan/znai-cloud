/**
 * Top Bar for mobile version
 * Height: 56px, sticky position
 */
import { Box } from '../common/Box';
import { ThreeBarsIcon, SearchIcon, BellIcon } from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';
import { authApi } from '../../services/api';

interface TopBarProps {
  onMenuClick: () => void;
  title?: string;
}

export function TopBar({ onMenuClick, title = 'Znai.cloud' }: TopBarProps) {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const user = authApi.getCurrentUser();

  return (
    <Box
      as="header"
      sx={{
        position: 'sticky',
        top: 0,
        left: 0,
        right: 0,
        height: '56px',
        backgroundColor: themeColors.bg.primary,
        borderBottom: `1px solid ${themeColors.border.primary}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        zIndex: 50,
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.12)',
      }}
    >
      {/* Left side: Hamburger menu + Logo + Title */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flex: 1,
          minWidth: 0,
        }}
      >
        <Box
          as="button"
          onClick={onMenuClick}
          sx={{
            background: 'transparent',
            border: 'none',
            padding: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: themeColors.text.primary,
            '&:hover': {
              backgroundColor: themeColors.bg.secondary,
              borderRadius: '6px',
            },
            '&:active': {
              transform: 'scale(0.95)',
            },
          }}
          aria-label="Open menu"
        >
          <ThreeBarsIcon size={24} />
        </Box>

        <Box
          sx={{
            fontSize: '16px',
            fontWeight: 600,
            color: themeColors.text.primary,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {title}
        </Box>
      </Box>

      {/* Right side: Search + Notifications + Avatar */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <Box
          as="button"
          sx={{
            background: 'transparent',
            border: 'none',
            padding: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: themeColors.text.secondary,
            '&:hover': {
              color: themeColors.text.primary,
              backgroundColor: themeColors.bg.secondary,
              borderRadius: '6px',
            },
          }}
          aria-label="Search"
        >
          <SearchIcon size={20} />
        </Box>

        <Box
          as="button"
          sx={{
            background: 'transparent',
            border: 'none',
            padding: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: themeColors.text.secondary,
            position: 'relative',
            '&:hover': {
              color: themeColors.text.primary,
              backgroundColor: themeColors.bg.secondary,
              borderRadius: '6px',
            },
          }}
          aria-label="Notifications"
        >
          <BellIcon size={20} />
          {/* Notification badge */}
          <Box
            sx={{
              position: 'absolute',
              top: '6px',
              right: '6px',
              width: '8px',
              height: '8px',
              backgroundColor: themeColors.accent.red,
              borderRadius: '50%',
            }}
          />
        </Box>

        <Box
          as="button"
          sx={{
            background: 'transparent',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-label="User menu"
        >
          <Box
            sx={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: colors[theme].accent.blue,
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              fontWeight: 600,
            }}
          >
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
