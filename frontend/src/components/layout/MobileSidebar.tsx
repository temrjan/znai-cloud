/**
 * Mobile Sidebar - Overlay menu with chat history
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
  PlusIcon,
  TrashIcon,
} from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';
import { authApi, adminApi, chatSessionsApi } from '../../services/api';
import { UserRole, ChatSession } from '../../types';

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  activeSessionId?: number;
  onSessionSelect?: (sessionId: number) => void;
  onNewChat?: () => void;
  refreshTrigger?: number;
}

export function MobileSidebar({
  isOpen,
  onClose,
  activeSessionId,
  onSessionSelect,
  onNewChat,
  refreshTrigger
}: MobileSidebarProps) {
  const { theme, toggleTheme } = useTheme();
  const themeColors = colors[theme];
  const navigate = useNavigate();
  const location = useLocation();
  const user = authApi.getCurrentUser();
  const [pendingCount, setPendingCount] = useState(0);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);

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

  // Load chat sessions
  useEffect(() => {
    if (isOpen && location.pathname === '/chat') {
      loadSessions();
    }
  }, [isOpen, refreshTrigger, location.pathname]);

  const loadSessions = async () => {
    setLoadingSessions(true);
    try {
      const response = await chatSessionsApi.list();
      setSessions(response.sessions);
    } catch (err) {
      console.error('Failed to load chat sessions:', err);
    } finally {
      setLoadingSessions(false);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: number) => {
    e.stopPropagation();
    try {
      await chatSessionsApi.delete(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        onNewChat?.();
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSessionClick = (sessionId: number) => {
    onSessionSelect?.(sessionId);
    onClose();
  };

  const handleNewChat = () => {
    onNewChat?.();
    onClose();
  };

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

        {/* Chat history (only on chat page) */}
        {location.pathname === '/chat' && (
          <Box
            sx={{
              padding: '8px',
              paddingTop: 0,
              borderTop: `1px solid ${themeColors.border.primary}`,
              marginTop: '8px',
            }}
          >
            {/* New chat button */}
            <Box
              as="button"
              onClick={handleNewChat}
              sx={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 12px',
                marginTop: '8px',
                background: 'linear-gradient(135deg, #1B3554 0%, #80AAD3 100%)',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: 500,
              }}
            >
              <PlusIcon size={16} />
              Новый чат
            </Box>

            {/* Chat history header */}
            <Box
              sx={{
                fontSize: '11px',
                fontWeight: 600,
                color: themeColors.text.tertiary,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                padding: '12px 12px 8px',
              }}
            >
              История чатов
            </Box>

            {/* Sessions list */}
            <Box
              sx={{
                maxHeight: '200px',
                overflowY: 'auto',
              }}
            >
              {loadingSessions ? (
                <Box
                  sx={{
                    padding: '12px',
                    fontSize: '13px',
                    color: themeColors.text.tertiary,
                    textAlign: 'center',
                  }}
                >
                  Загрузка...
                </Box>
              ) : sessions.length === 0 ? (
                <Box
                  sx={{
                    padding: '12px',
                    fontSize: '13px',
                    color: themeColors.text.tertiary,
                    textAlign: 'center',
                  }}
                >
                  Нет истории чатов
                </Box>
              ) : (
                sessions.map((session) => (
                  <Box
                    key={session.id}
                    as="button"
                    onClick={() => handleSessionClick(session.id)}
                    sx={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '8px',
                      padding: '10px 12px',
                      backgroundColor: activeSessionId === session.id
                        ? themeColors.bg.secondary
                        : 'transparent',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      color: themeColors.text.primary,
                      fontSize: '13px',
                      textAlign: 'left',
                      '&:hover': {
                        backgroundColor: themeColors.bg.secondary,
                      },
                    }}
                  >
                    <Box
                      sx={{
                        flex: 1,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {session.title}
                    </Box>
                    <Box
                      as="button"
                      onClick={(e: React.MouseEvent) => handleDeleteSession(e, session.id)}
                      sx={{
                        background: 'transparent',
                        border: 'none',
                        padding: '4px',
                        cursor: 'pointer',
                        color: themeColors.text.tertiary,
                        display: 'flex',
                        alignItems: 'center',
                        flexShrink: 0,
                        '&:hover': {
                          color: themeColors.accent.red,
                        },
                      }}
                    >
                      <TrashIcon size={14} />
                    </Box>
                  </Box>
                ))
              )}
            </Box>
          </Box>
        )}

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
