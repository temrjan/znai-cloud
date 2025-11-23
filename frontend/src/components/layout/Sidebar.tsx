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
  TrashIcon,
  SignOutIcon,
} from '@primer/octicons-react';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../styles/theme';
import { authApi, adminApi, chatSessionsApi } from '../../services/api';
import { UserRole, ChatSession } from '../../types';

interface SidebarProps {
  activeSessionId?: number;
  onSessionSelect?: (sessionId: number) => void;
  onNewChat?: () => void;
  refreshTrigger?: number;
}

export function Sidebar({ activeSessionId, onSessionSelect, onNewChat, refreshTrigger }: SidebarProps) {
  const { theme, toggleTheme } = useTheme();
  const themeColors = colors[theme];
  const navigate = useNavigate();
  const location = useLocation();
  const user = authApi.getCurrentUser();
  const [pendingCount, setPendingCount] = useState(0);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [hoveredSessionId, setHoveredSessionId] = useState<number | null>(null);

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
      const interval = setInterval(loadPendingCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  // Load chat sessions
  useEffect(() => {
    const loadSessions = async () => {
      setSessionsLoading(true);
      try {
        const response = await chatSessionsApi.list();
        setSessions(response.sessions);
      } catch (err) {
        console.error('Failed to load chat sessions:', err);
      } finally {
        setSessionsLoading(false);
      }
    };

    loadSessions();
  }, [refreshTrigger]);

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: number) => {
    e.stopPropagation();
    if (!confirm('Удалить этот чат?')) return;

    try {
      await chatSessionsApi.delete(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (activeSessionId === sessionId && onNewChat) {
        onNewChat();
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
    } else {
      navigate('/chat');
    }
  };

  const handleSessionClick = (sessionId: number) => {
    if (onSessionSelect) {
      onSessionSelect(sessionId);
    }
  };

  return (
    <Box
      sx={{
        width: '240px',
        height: '100vh',
        backgroundColor: themeColors.bg.primary,
        borderRight: `1px solid ${themeColors.border.primary}`,
        display: 'flex',
        flexDirection: 'column',
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
          flexShrink: 0,
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
          onClick={handleNewChat}
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
          Новый чат
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ padding: '8px', flexShrink: 0 }}>
        <NavItem
          icon={CommentDiscussionIcon}
          label="Чат"
          active={isActive('/chat')}
          onClick={() => navigate('/chat')}
          themeColors={themeColors}
        />
        <NavItem
          icon={FileIcon}
          label="Документы"
          active={isActive('/documents')}
          onClick={() => navigate('/documents')}
          themeColors={themeColors}
        />
        {user?.role === UserRole.ADMIN && (
          <NavItem
            icon={ShieldLockIcon}
            label="Админ"
            active={isActive('/admin')}
            onClick={() => navigate('/admin')}
            themeColors={themeColors}
            badge={pendingCount > 0 ? pendingCount : undefined}
          />
        )}
      </Box>

      {/* Divider */}
      <Box
        sx={{
          height: '1px',
          backgroundColor: themeColors.border.primary,
          margin: '8px 16px',
          flexShrink: 0,
        }}
      />

      {/* Chat History Section */}
      <Box
        sx={{
          flex: 1,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
        }}
      >
        <Box
          sx={{
            padding: '8px 16px',
            fontSize: '12px',
            fontWeight: 500,
            color: themeColors.text.tertiary,
            textTransform: 'uppercase',
            flexShrink: 0,
          }}
        >
          История чатов
        </Box>

        {/* Scrollable sessions list */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            padding: '0 8px 8px 8px',
          }}
        >
          {sessionsLoading ? (
            <Box sx={{ padding: '8px 12px', color: themeColors.text.tertiary, fontSize: '13px' }}>
              Загрузка...
            </Box>
          ) : sessions.length === 0 ? (
            <Box sx={{ padding: '8px 12px', color: themeColors.text.tertiary, fontSize: '13px' }}>
              Нет истории
            </Box>
          ) : (
            sessions.map(session => (
              <Box
                key={session.id}
                as="button"
                onClick={() => handleSessionClick(session.id)}
                onMouseEnter={() => setHoveredSessionId(session.id)}
                onMouseLeave={() => setHoveredSessionId(null)}
                sx={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 12px',
                  backgroundColor: activeSessionId === session.id ? themeColors.bg.secondary : 'transparent',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  color: activeSessionId === session.id ? themeColors.text.primary : themeColors.text.secondary,
                  fontSize: '13px',
                  textAlign: 'left',
                  margin: '2px 0',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: themeColors.bg.secondary,
                    color: themeColors.text.primary,
                  },
                }}
              >
                <Box
                  sx={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: activeSessionId === session.id
                      ? themeColors.accent.blue
                      : themeColors.text.tertiary,
                    flexShrink: 0,
                  }}
                />
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
                {hoveredSessionId === session.id && (
                  <Box
                    as="span"
                    onClick={(e: React.MouseEvent) => handleDeleteSession(e, session.id)}
                    sx={{
                      padding: '2px',
                      color: themeColors.text.tertiary,
                      cursor: 'pointer',
                      flexShrink: 0,
                      '&:hover': {
                        color: themeColors.accent.red,
                      },
                    }}
                  >
                    <TrashIcon size={14} />
                  </Box>
                )}
              </Box>
            ))
          )}
        </Box>
      </Box>

      {/* Footer */}
      <Box
        sx={{
          padding: '16px',
          borderTop: `1px solid ${themeColors.border.primary}`,
          flexShrink: 0,
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
          <span>{theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}</span>
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

        {/* Logout button */}
        <Box
          as="button"
          onClick={() => {
            authApi.logout();
            navigate('/login');
          }}
          sx={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 12px',
            marginTop: '8px',
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            color: themeColors.text.tertiary,
            fontSize: '13px',
            '&:hover': {
              backgroundColor: themeColors.bg.secondary,
              color: themeColors.accent.red,
            },
          }}
        >
          <SignOutIcon size={16} />
          <span>Выйти</span>
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
