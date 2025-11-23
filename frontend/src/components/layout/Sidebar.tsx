/**
 * Desktop Sidebar - Left panel with navigation and chat history
 * Width: 240px, fixed position
 */
import { useState, useEffect } from 'react';
import { Box } from '../common/Box';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  PencilIcon,
  CommentDiscussionIcon,
  FileIcon,
  ShieldLockIcon,
  SunIcon,
  MoonIcon,
} from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';
import { authApi, adminApi } from '../../services/api';
import { UserRole } from '../../types';

export function Sidebar() {
  const { theme, toggleTheme } = useTheme();
  const themeColors = colors[theme];
  const navigate = useNavigate();
  const location = useLocation();
  const user = authApi.getCurrentUser();
  const [pendingCount, setPendingCount] = useState(0);

  const isActive = (path: string) => location.pathname === path;

  // Load pending users count for admins
  useEffect(() => {
    if (user?.role === UserRole.ADMIN) {
      const loadPendingCount = async () => {
        try {
          const users = await adminApi.getPendingUsers();
          setPendingCount(users.length);
        } catch (err) {
          console.error('Failed to load pending users count:', err);
        }
      };

      loadPendingCount();
      // Refresh every 30 seconds
      const interval = setInterval(loadPendingCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  return (
    <Box
      sx={{
        width: '240px',
        height: '100vh',
        backgroundColor: themeColors.bg.primary,
        borderRight: `1px solid ${themeColors.border.primary}`,
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        position: 'fixed',
        left: 0,
        top: 0,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          padding: '16px',
          borderBottom: `1px solid ${themeColors.border.primary}`,
        }}
      >
        <Box
          sx={{
            fontSize: '18px',
            fontWeight: 600,
            color: themeColors.text.primary,
            marginBottom: '12px',
          }}
        >
          Znai.cloud
        </Box>

        {/* New chat button */}
        <Box
          as="button"
          onClick={() => navigate('/chat')}
          sx={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-start',
            gap: '8px',
            padding: '8px 12px',
            background: themeColors.accent.blueGradient,
            color: '#ffffff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer',
            '&:hover': {
              opacity: 0.9,
            },
          }}
        >
          <PencilIcon size={16} />
          New chat
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ padding: '8px' }}>
        <NavItem
          icon={CommentDiscussionIcon}
          label="Chat"
          active={isActive('/chat')}
          onClick={() => navigate('/chat')}
          themeColors={themeColors}
        />
        <NavItem
          icon={FileIcon}
          label="Documents"
          active={isActive('/documents')}
          onClick={() => navigate('/documents')}
          themeColors={themeColors}
        />
        {user?.role === UserRole.ADMIN && (
          <NavItem
            icon={ShieldLockIcon}
            label="Admin"
            active={isActive('/admin')}
            onClick={() => navigate('/admin')}
            themeColors={themeColors}
            badge={pendingCount > 0 ? pendingCount : undefined}
          />
        )}
      </Box>

      {/* Spacer */}
      <Box sx={{ flex: 1 }} />

      {/* Footer */}
      <Box
        sx={{
          padding: '16px',
          borderTop: `1px solid ${themeColors.border.primary}`,
        }}
      >
        {/* Theme toggle */}
        <Box
          as="button"
          onClick={toggleTheme}
          sx={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 12px',
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            color: themeColors.text.secondary,
            fontSize: '14px',
            '&:hover': {
              backgroundColor: themeColors.bg.secondary,
              color: themeColors.text.primary,
            },
          }}
        >
          {theme === 'dark' ? <SunIcon size={16} /> : <MoonIcon size={16} />}
          <span>{theme === 'dark' ? 'Light mode' : 'Dark mode'}</span>
        </Box>

        {/* User info */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginTop: '12px',
            padding: '8px',
            borderRadius: '6px',
            '&:hover': {
              backgroundColor: themeColors.bg.secondary,
            },
          }}
        >
          <Box
            sx={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: themeColors.accent.blue,
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              fontWeight: 600,
              flexShrink: 0,
            }}
          >
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </Box>
          <Box
            sx={{
              flex: 1,
              minWidth: 0,
            }}
          >
            <Box
              sx={{
                fontSize: '14px',
                fontWeight: 500,
                color: themeColors.text.primary,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user?.full_name || 'User'}
            </Box>
            <Box
              sx={{
                fontSize: '12px',
                color: themeColors.text.tertiary,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user?.email}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

// Nav item component
interface NavItemProps {
  icon: React.ComponentType<any>;
  label: string;
  active?: boolean;
  onClick?: () => void;
  themeColors: (typeof colors)['dark'] | (typeof colors)['light'];
  badge?: number;
}

function NavItem({ icon: Icon, label, active, onClick, themeColors, badge }: NavItemProps) {
  return (
    <Box
      as="button"
      onClick={onClick}
      sx={{
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '6px 12px',
        backgroundColor: active ? themeColors.bg.secondary : 'transparent',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        color: active ? themeColors.text.primary : themeColors.text.secondary,
        fontSize: '14px',
        fontWeight: active ? 500 : 400,
        textAlign: 'left',
        margin: '2px 0',
        position: 'relative',
        '&:hover': {
          backgroundColor: themeColors.bg.secondary,
          color: themeColors.text.primary,
        },
      }}
    >
      <Icon size={16} />
      <span style={{ flex: 1 }}>{label}</span>
      {badge !== undefined && (
        <Box
          sx={{
            minWidth: '18px',
            height: '18px',
            padding: '0 5px',
            backgroundColor: themeColors.accent.red,
            color: '#ffffff',
            borderRadius: '9px',
            fontSize: '11px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          {badge}
        </Box>
      )}
    </Box>
  );
}

