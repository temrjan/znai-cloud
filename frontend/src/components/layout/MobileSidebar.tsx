/**
 * Mobile Sidebar - Overlay menu
 * Slides in from left, 80vw width (max 320px)
 */
import { useEffect, useState } from 'react';
import { Box } from '../common/Box';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  XIcon,
  CommentDiscussionIcon,
  SunIcon,
  MoonIcon,
  FileIcon,
  ShieldLockIcon,
} from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';
import { authApi, adminApi } from '../../services/api';
import { UserRole } from '../../types';

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileSidebar({ isOpen, onClose }: MobileSidebarProps) {
  const { theme, toggleTheme } = useTheme();
  const themeColors = colors[theme];
  const navigate = useNavigate();
  const location = useLocation();
  const user = authApi.getCurrentUser();
  const [pendingCount, setPendingCount] = useState(0);

  // Load pending users count for admins
  useEffect(() => {
    if (user?.role === UserRole.ADMIN && isOpen) {
      const loadPendingCount = async () => {
        try {
          const users = await adminApi.getPendingUsers();
          setPendingCount(users.length);
        } catch (err) {
          console.error('Failed to load pending users count:', err);
        }
      };
      loadPendingCount();
    }
  }, [user, isOpen]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleNavigate = (path: string) => {
    navigate(path);
    onClose();
  };

  const isActive = (path: string) => location.pathname === path;

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay background */}
      <Box
        onClick={onClose}
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 200,
          animation: 'fadeIn 0.3s ease-out',
          '@keyframes fadeIn': {
            from: { opacity: 0 },
            to: { opacity: 1 },
          },
        }}
      />

      {/* Sidebar panel */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          bottom: 0,
          width: '80vw',
          maxWidth: '320px',
          backgroundColor: themeColors.bg.primary,
          zIndex: 201,
          overflowY: 'auto',
          animation: 'slideInLeft 0.3s ease-out',
          '@keyframes slideInLeft': {
            from: { transform: 'translateX(-100%)' },
            to: { transform: 'translateX(0)' },
          },
        }}
      >
        {/* Header */}
        <Box
          sx={{
            height: '56px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 16px',
            borderBottom: `1px solid ${themeColors.border.primary}`,
          }}
        >
          <Box
            sx={{
              fontSize: '16px',
              fontWeight: 600,
              color: themeColors.text.primary,
            }}
          >
            Znai.cloud
          </Box>
          <Box
            as="button"
            onClick={onClose}
            sx={{
              background: 'transparent',
              border: 'none',
              padding: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              color: themeColors.text.secondary,
              '&:hover': {
                color: themeColors.text.primary,
              },
            }}
            aria-label="Close menu"
          >
            <XIcon size={24} />
          </Box>
        </Box>

        {/* Menu items */}
        <Box sx={{ padding: '8px' }}>
          {/* Main navigation */}
          <MenuItem
            icon={CommentDiscussionIcon}
            label="Chat"
            active={isActive('/chat')}
            onClick={() => handleNavigate('/chat')}
            themeColors={themeColors}
          />
          <MenuItem
            icon={FileIcon}
            label="Documents"
            active={isActive('/documents')}
            onClick={() => handleNavigate('/documents')}
            themeColors={themeColors}
          />
          {user?.role === UserRole.ADMIN && (
            <MenuItem
              icon={ShieldLockIcon}
              label="Admin"
              active={isActive('/admin')}
              onClick={() => handleNavigate('/admin')}
              themeColors={themeColors}
              badge={pendingCount > 0 ? pendingCount : undefined}
            />
          )}
        </Box>

        {/* Footer */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '16px',
            borderTop: `1px solid ${themeColors.border.primary}`,
            backgroundColor: themeColors.bg.primary,
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
              padding: '12px',
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              color: themeColors.text.secondary,
              '&:hover': {
                backgroundColor: themeColors.bg.secondary,
                color: themeColors.text.primary,
              },
            }}
          >
            {theme === 'dark' ? <SunIcon size={20} /> : <MoonIcon size={20} />}
            <Box sx={{ fontSize: '14px' }}>{theme === 'dark' ? 'Light mode' : 'Dark mode'}</Box>
          </Box>

          {/* User info */}
          <Box
            sx={{
              marginTop: '12px',
              fontSize: '12px',
              color: themeColors.text.secondary,
            }}
          >
            {user?.email}
          </Box>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '8px',
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
              }}
            >
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </Box>
            <Box
              sx={{
                fontSize: '14px',
                color: themeColors.text.primary,
                fontWeight: 500,
              }}
            >
              {user?.full_name || 'User'}
            </Box>
          </Box>
        </Box>
      </Box>
    </>
  );
}

// Menu item component
interface MenuItemProps {
  icon: React.ComponentType<any>;
  label: string;
  active?: boolean;
  onClick?: () => void;
  themeColors: (typeof colors)['dark'] | (typeof colors)['light'];
  badge?: number;
}

function MenuItem({ icon: Icon, label, active, onClick, themeColors, badge }: MenuItemProps) {
  return (
    <Box
      as="button"
      onClick={onClick}
      sx={{
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px',
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
      <Icon size={20} />
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
