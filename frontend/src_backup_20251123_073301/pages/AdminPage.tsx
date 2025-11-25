/**
 * Admin page - GitHub Copilot style
 */
import { useState, useEffect } from 'react';
import { Box } from '../components/common/Box';
import { useTheme } from '../contexts/ThemeContext';
import { useIsMobile, useIsDesktop } from '../hooks/useMediaQuery';
import { colors } from '../styles/theme';
import { adminApi } from '../services/api';
import { User } from '../types';
import {
  CheckIcon,
  XIcon,
  PersonIcon,
} from '@primer/octicons-react';

// Layout components
import { TopBar } from '../components/layout/TopBar';
import { MobileSidebar } from '../components/layout/MobileSidebar';
import { Sidebar } from '../components/layout/Sidebar';

export function AdminPage() {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const isMobile = useIsMobile();
  const isDesktop = useIsDesktop();

  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadPendingUsers();
  }, []);

  // Auto-clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const loadPendingUsers = async () => {
    try {
      const users = await adminApi.getPendingUsers();
      setPendingUsers(users);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load pending users');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId: string) => {
    try {
      await adminApi.approveUser(userId);
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve user');
    }
  };

  const handleReject = async (userId: string, email: string) => {
    if (!confirm(`Reject user ${email}?`)) return;

    try {
      await adminApi.rejectUser(userId);
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reject user');
    }
  };

  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        backgroundColor: themeColors.bg.primary,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Mobile: TopBar */}
      {isMobile && (
        <TopBar
          onMenuClick={() => setMobileMenuOpen(true)}
          title="Admin"
        />
      )}

      {/* Mobile: Sidebar overlay */}
      {isMobile && (
        <MobileSidebar
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Desktop: Fixed Sidebar */}
      {isDesktop && <Sidebar />}

      {/* Main content area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          marginLeft: isDesktop ? '240px' : 0,
          height: isMobile ? 'calc(100vh - 56px)' : '100vh',
          overflowY: 'auto',
        }}
      >
        <Box
          sx={{
            maxWidth: '900px',
            width: '100%',
            margin: '0 auto',
            padding: isMobile ? '16px' : '32px 24px',
          }}
        >
          {/* Header */}
          <Box sx={{ marginBottom: '24px' }}>
            <Box
              sx={{
                fontSize: isMobile ? '24px' : '28px',
                fontWeight: 600,
                color: themeColors.text.primary,
                marginBottom: '8px',
              }}
            >
              User Approvals
            </Box>
            <Box
              sx={{
                fontSize: '14px',
                color: themeColors.text.secondary,
              }}
            >
              {pendingUsers.length === 0
                ? 'No pending registrations'
                : `${pendingUsers.length} user${pendingUsers.length === 1 ? '' : 's'} waiting for approval`}
            </Box>
          </Box>

          {/* Error message */}
          {error && (
            <Box
              sx={{
                padding: '12px 16px',
                backgroundColor: themeColors.accent.red,
                color: '#ffffff',
                borderRadius: '6px',
                fontSize: '14px',
                marginBottom: '16px',
              }}
            >
              {error}
            </Box>
          )}

          {/* Users list */}
          {loading ? (
            <Box
              sx={{
                textAlign: 'center',
                padding: '48px',
                color: themeColors.text.secondary,
                fontSize: '14px',
              }}
            >
              Loading pending users...
            </Box>
          ) : pendingUsers.length === 0 ? (
            <Box
              sx={{
                padding: '48px',
                textAlign: 'center',
                backgroundColor: themeColors.bg.secondary,
                border: `1px solid ${themeColors.border.primary}`,
                borderRadius: '8px',
              }}
            >
              <Box sx={{ marginBottom: '16px', color: themeColors.text.secondary }}>
                <PersonIcon size={48} />
              </Box>
              <Box
                sx={{
                  fontSize: '18px',
                  fontWeight: 500,
                  color: themeColors.text.primary,
                  marginBottom: '8px',
                }}
              >
                No pending approvals
              </Box>
              <Box sx={{ fontSize: '14px', color: themeColors.text.secondary }}>
                All user registrations have been processed
              </Box>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {pendingUsers.map((user) => (
                <UserCard
                  key={user.id}
                  user={user}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  themeColors={themeColors}
                />
              ))}
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}

// User card component
interface UserCardProps {
  user: User;
  onApprove: (userId: string) => void;
  onReject: (userId: string, email: string) => void;
  themeColors: (typeof colors)['dark'] | (typeof colors)['light'];
}

function UserCard({ user, onApprove, onReject, themeColors }: UserCardProps) {
  return (
    <Box
      sx={{
        padding: '16px',
        backgroundColor: themeColors.bg.secondary,
        border: `1px solid ${themeColors.border.primary}`,
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        flexWrap: 'wrap',
      }}
    >
      {/* Left: User info */}
      <Box sx={{ flex: 1, minWidth: '200px' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <PersonIcon size={16} />
          <Box
            sx={{
              fontSize: '14px',
              fontWeight: 500,
              color: themeColors.text.primary,
            }}
          >
            {user.full_name}
          </Box>
        </Box>
        <Box
          sx={{
            fontSize: '13px',
            color: themeColors.text.secondary,
            marginBottom: '4px',
          }}
        >
          {user.email}
        </Box>
        <Box
          sx={{
            fontSize: '12px',
            color: themeColors.text.tertiary,
          }}
        >
          Registered: {new Date(user.created_at).toLocaleString()}
        </Box>
      </Box>

      {/* Right: Actions */}
      <Box sx={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
        {/* Approve button */}
        <Box
          as="button"
          onClick={() => onApprove(user.id)}
          sx={{
            padding: '8px 16px',
            backgroundColor: themeColors.accent.green,
            color: '#ffffff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            '&:hover': {
              opacity: 0.9,
            },
          }}
        >
          <CheckIcon size={14} />
          Approve
        </Box>

        {/* Reject button */}
        <Box
          as="button"
          onClick={() => onReject(user.id, user.email)}
          sx={{
            padding: '8px 16px',
            backgroundColor: 'transparent',
            color: themeColors.text.secondary,
            border: `1px solid ${themeColors.border.primary}`,
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            '&:hover': {
              backgroundColor: themeColors.accent.red,
              borderColor: themeColors.accent.red,
              color: '#ffffff',
            },
          }}
        >
          <XIcon size={14} />
          Reject
        </Box>
      </Box>
    </Box>
  );
}
