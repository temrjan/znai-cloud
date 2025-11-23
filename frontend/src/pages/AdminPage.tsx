/**
 * Admin page - Platform owner dashboard
 */
import { useState, useEffect } from 'react';
import { Box } from '../components/common/Box';
import { useTheme } from '../contexts/ThemeContext';
import { useIsMobile, useIsDesktop } from '../hooks/useMediaQuery';
import { colors } from '../styles/theme';
import { adminApi } from '../services/api';
import { User, PendingOrganization } from '../types';
import {
  CheckIcon,
  XIcon,
  PersonIcon,
  OrganizationIcon,
} from '@primer/octicons-react';

// Layout components
import { TopBar } from '../components/layout/TopBar';
import { MobileSidebar } from '../components/layout/MobileSidebar';
import { Sidebar } from '../components/layout/Sidebar';

type TabType = 'organizations' | 'users';

export function AdminPage() {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const isMobile = useIsMobile();
  const isDesktop = useIsDesktop();

  const [activeTab, setActiveTab] = useState<TabType>('organizations');
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [pendingOrgs, setPendingOrgs] = useState<PendingOrganization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const loadData = async () => {
    try {
      const [users, orgs] = await Promise.all([
        adminApi.getPendingUsers(),
        adminApi.getPendingOrganizations(),
      ]);
      setPendingUsers(users);
      setPendingOrgs(orgs);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveUser = async (userId: string) => {
    try {
      await adminApi.approveUser(userId);
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка подтверждения');
    }
  };

  const handleRejectUser = async (userId: string, email: string) => {
    if (!confirm(`Отклонить пользователя ${email}?`)) return;
    try {
      await adminApi.rejectUser(userId);
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отклонения');
    }
  };

  const handleApproveOrg = async (orgId: number) => {
    try {
      await adminApi.approveOrganization(orgId);
      setPendingOrgs(pendingOrgs.filter((o) => o.id !== orgId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка подтверждения');
    }
  };

  const handleRejectOrg = async (orgId: number, name: string) => {
    if (!confirm(`Отклонить организацию "${name}"?`)) return;
    try {
      await adminApi.rejectOrganization(orgId);
      setPendingOrgs(pendingOrgs.filter((o) => o.id !== orgId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отклонения');
    }
  };

  const totalPending = pendingUsers.length + pendingOrgs.length;

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
      {isMobile && (
        <TopBar
          onMenuClick={() => setMobileMenuOpen(true)}
          title="Admin"
        />
      )}

      {isMobile && (
        <MobileSidebar
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        />
      )}

      {isDesktop && <Sidebar />}

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
              Панель управления
            </Box>
            <Box sx={{ fontSize: '14px', color: themeColors.text.secondary }}>
              {totalPending === 0
                ? 'Нет ожидающих заявок'
                : `${totalPending} заявок ожидают рассмотрения`}
            </Box>
          </Box>

          {/* Error */}
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

          {/* Tabs */}
          <Box
            sx={{
              display: 'flex',
              gap: '8px',
              marginBottom: '24px',
              borderBottom: `1px solid ${themeColors.border.primary}`,
              paddingBottom: '12px',
            }}
          >
            <Box
              as="button"
              onClick={() => setActiveTab('organizations')}
              sx={{
                padding: '8px 16px',
                backgroundColor: activeTab === 'organizations' ? themeColors.accent.blueGradient : 'transparent',
                color: activeTab === 'organizations' ? '#ffffff' : themeColors.text.secondary,
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <OrganizationIcon size={16} />
              Организации
              {pendingOrgs.length > 0 && (
                <Box
                  sx={{
                    backgroundColor: '#ff4444',
                    color: '#ffffff',
                    borderRadius: '10px',
                    padding: '2px 8px',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                >
                  {pendingOrgs.length}
                </Box>
              )}
            </Box>
            <Box
              as="button"
              onClick={() => setActiveTab('users')}
              sx={{
                padding: '8px 16px',
                backgroundColor: activeTab === 'users' ? themeColors.accent.blueGradient : 'transparent',
                color: activeTab === 'users' ? '#ffffff' : themeColors.text.secondary,
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <PersonIcon size={16} />
              Пользователи
              {pendingUsers.length > 0 && (
                <Box
                  sx={{
                    backgroundColor: '#ff4444',
                    color: '#ffffff',
                    borderRadius: '10px',
                    padding: '2px 8px',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                >
                  {pendingUsers.length}
                </Box>
              )}
            </Box>
          </Box>

          {/* Content */}
          {loading ? (
            <Box sx={{ textAlign: 'center', padding: '48px', color: themeColors.text.secondary }}>
              Загрузка...
            </Box>
          ) : (
            <>
              {/* Organizations Tab */}
              {activeTab === 'organizations' && (
                pendingOrgs.length === 0 ? (
                  <EmptyState
                    icon={<OrganizationIcon size={48} />}
                    title="Нет заявок от организаций"
                    description="Все заявки на регистрацию организаций обработаны"
                    themeColors={themeColors}
                  />
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {pendingOrgs.map((org) => (
                      <OrganizationCard
                        key={org.id}
                        org={org}
                        onApprove={handleApproveOrg}
                        onReject={handleRejectOrg}
                        themeColors={themeColors}
                      />
                    ))}
                  </Box>
                )
              )}

              {/* Users Tab */}
              {activeTab === 'users' && (
                pendingUsers.length === 0 ? (
                  <EmptyState
                    icon={<PersonIcon size={48} />}
                    title="Нет заявок от пользователей"
                    description="Все личные регистрации обработаны"
                    themeColors={themeColors}
                  />
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {pendingUsers.map((user) => (
                      <UserCard
                        key={user.id}
                        user={user}
                        onApprove={handleApproveUser}
                        onReject={handleRejectUser}
                        themeColors={themeColors}
                      />
                    ))}
                  </Box>
                )
              )}
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
}

// Empty state component
function EmptyState({
  icon,
  title,
  description,
  themeColors,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  themeColors: any;
}) {
  return (
    <Box
      sx={{
        padding: '48px',
        textAlign: 'center',
        backgroundColor: themeColors.bg.secondary,
        border: `1px solid ${themeColors.border.primary}`,
        borderRadius: '8px',
      }}
    >
      <Box sx={{ marginBottom: '16px', color: themeColors.text.secondary }}>{icon}</Box>
      <Box sx={{ fontSize: '18px', fontWeight: 500, color: themeColors.text.primary, marginBottom: '8px' }}>
        {title}
      </Box>
      <Box sx={{ fontSize: '14px', color: themeColors.text.secondary }}>{description}</Box>
    </Box>
  );
}

// Organization card
function OrganizationCard({
  org,
  onApprove,
  onReject,
  themeColors,
}: {
  org: PendingOrganization;
  onApprove: (id: number) => void;
  onReject: (id: number, name: string) => void;
  themeColors: any;
}) {
  return (
    <Box
      sx={{
        padding: '20px',
        backgroundColor: themeColors.bg.secondary,
        border: `1px solid ${themeColors.border.primary}`,
        borderRadius: '8px',
      }}
    >
      {/* Organization name */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
        <OrganizationIcon size={20} />
        <Box sx={{ fontSize: '18px', fontWeight: 600, color: themeColors.text.primary }}>
          {org.name}
        </Box>
      </Box>

      {/* Owner info */}
      <Box sx={{ marginBottom: '16px', padding: '12px', backgroundColor: themeColors.bg.tertiary, borderRadius: '6px' }}>
        <Box sx={{ fontSize: '12px', color: themeColors.text.tertiary, marginBottom: '4px' }}>
          Администратор организации:
        </Box>
        <Box sx={{ fontSize: '14px', fontWeight: 500, color: themeColors.text.primary }}>
          {org.owner_full_name || 'Без имени'}
        </Box>
        <Box sx={{ fontSize: '13px', color: themeColors.text.secondary }}>
          {org.owner_email}
        </Box>
      </Box>

      {/* Date and actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <Box sx={{ fontSize: '12px', color: themeColors.text.tertiary }}>
          Заявка от {new Date(org.created_at).toLocaleString('ru-RU')}
        </Box>
        <Box sx={{ display: 'flex', gap: '8px' }}>
          <Box
            as="button"
            onClick={() => onApprove(org.id)}
            sx={{
              padding: '8px 20px',
              backgroundColor: themeColors.accent.green,
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              '&:hover': { opacity: 0.9 },
            }}
          >
            <CheckIcon size={14} />
            Подтвердить
          </Box>
          <Box
            as="button"
            onClick={() => onReject(org.id, org.name)}
            sx={{
              padding: '8px 20px',
              backgroundColor: 'transparent',
              color: themeColors.text.secondary,
              border: `1px solid ${themeColors.border.primary}`,
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              '&:hover': { backgroundColor: themeColors.accent.red, borderColor: themeColors.accent.red, color: '#ffffff' },
            }}
          >
            <XIcon size={14} />
            Отклонить
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

// User card
function UserCard({
  user,
  onApprove,
  onReject,
  themeColors,
}: {
  user: User;
  onApprove: (userId: string) => void;
  onReject: (userId: string, email: string) => void;
  themeColors: any;
}) {
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
      <Box sx={{ flex: 1, minWidth: '200px' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <PersonIcon size={16} />
          <Box sx={{ fontSize: '14px', fontWeight: 500, color: themeColors.text.primary }}>
            {user.full_name || 'Без имени'}
          </Box>
        </Box>
        <Box sx={{ fontSize: '13px', color: themeColors.text.secondary, marginBottom: '4px' }}>
          {user.email}
        </Box>
        <Box sx={{ fontSize: '12px', color: themeColors.text.tertiary }}>
          {new Date(user.created_at).toLocaleString('ru-RU')}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
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
            '&:hover': { opacity: 0.9 },
          }}
        >
          <CheckIcon size={14} />
          Подтвердить
        </Box>
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
            '&:hover': { backgroundColor: themeColors.accent.red, borderColor: themeColors.accent.red, color: '#ffffff' },
          }}
        >
          <XIcon size={14} />
          Отклонить
        </Box>
      </Box>
    </Box>
  );
}
