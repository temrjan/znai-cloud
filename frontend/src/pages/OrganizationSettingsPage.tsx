/**
 * Organization settings page - GitHub Copilot style with sidebar
 */
import { useState, useEffect } from "react";
import { Box } from "../components/common/Box";
import { useTheme } from "../contexts/ThemeContext";
import { useIsMobile, useIsDesktop } from "../hooks/useMediaQuery";
import { colors } from "../styles/theme";
import { organizationsApi, authApi, telegramBotApi } from "../services/api";
import {
  PeopleIcon,
  GearIcon,
  LinkIcon,
  TrashIcon,
  CopyIcon,
  CheckIcon,
} from "@primer/octicons-react";
import type {
  Organization,
  OrganizationMember,
  OrganizationInvite,
  OrganizationStats,
} from "../types";

// Layout components
import { TopBar } from "../components/layout/TopBar";
import { MobileSidebar } from "../components/layout/MobileSidebar";
import { Sidebar } from "../components/layout/Sidebar";

type TabType = "members" | "invites" | "settings" | "telegram";

export function OrganizationSettingsPage() {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const isMobile = useIsMobile();
  const isDesktop = useIsDesktop();

  const currentUser = authApi.getCurrentUser();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const [activeTab, setActiveTab] = useState<TabType>("members");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [organization, setOrganization] = useState<Organization | null>(null);
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [invites, setInvites] = useState<OrganizationInvite[]>([]);
  const [stats, setStats] = useState<OrganizationStats | null>(null);

  // Invite form
  const [inviteMaxUses, setInviteMaxUses] = useState(5);
  const [inviteExpiresDays, setInviteExpiresDays] = useState(7);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  // Settings form
  const [settingsForm, setSettingsForm] = useState({
    custom_system_prompt: "",
    custom_temperature: 0.7,
    response_language: "ru",
  });

  // Telegram bot
  const [telegramBot, setTelegramBot] = useState<{
    enabled: boolean;
    bot_username: string | null;
    webhook_url: string | null;
  }>({ enabled: false, bot_username: null, webhook_url: null });
  const [botToken, setBotToken] = useState("");
  const [botLoading, setBotLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  // Auto-clear messages
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [org, membersData, invitesData, settingsData, statsData, botStatus] =
        await Promise.all([
          organizationsApi.getMyOrganization(),
          organizationsApi.getMembers(),
          organizationsApi.getInvites().catch(() => []),
          organizationsApi.getSettings(),
          organizationsApi.getStats(),
          telegramBotApi.getStatus().catch(() => ({ enabled: false, bot_username: null, webhook_url: null })),
        ]);

      setOrganization(org);
      setMembers(membersData);
      setInvites(invitesData);
      setStats(statsData);
      setTelegramBot(botStatus);

      setSettingsForm({
        custom_system_prompt: settingsData.custom_system_prompt || "",
        custom_temperature: settingsData.custom_temperature || 0.7,
        response_language: settingsData.response_language || "ru",
      });
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError("У вас нет организации");
      } else {
        setError("Ошибка загрузки данных");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveMember = async (userId: number) => {
    if (!confirm("Удалить участника из организации?")) return;
    try {
      await organizationsApi.removeMember(userId);
      setMembers(members.filter((m) => m.user_id !== userId));
      setSuccess("Участник удален");
    } catch {
      setError("Ошибка удаления участника");
    }
  };

  const handleCreateInvite = async () => {
    try {
      const invite = await organizationsApi.createInvite({
        max_uses: inviteMaxUses,
        expires_in_days: inviteExpiresDays,
      });
      setInvites([invite, ...invites]);
      setSuccess("Приглашение создано");
    } catch {
      setError("Ошибка создания приглашения");
    }
  };

  const handleRevokeInvite = async (inviteId: number) => {
    try {
      await organizationsApi.revokeInvite(inviteId);
      setInvites(invites.filter((i) => i.id !== inviteId));
      setSuccess("Приглашение отозвано");
    } catch {
      setError("Ошибка отзыва приглашения");
    }
  };

  const handleCopyInviteLink = (code: string) => {
    const link = `${window.location.origin}/register?invite=${code}`;
    navigator.clipboard.writeText(link);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const handleSaveSettings = async () => {
    try {
      await organizationsApi.updateSettings(settingsForm);
      setSuccess("Настройки сохранены");
    } catch {
      setError("Ошибка сохранения настроек");
    }
  };

  const handleSetupTelegramBot = async () => {
    if (!botToken.trim()) {
      setError("Введите токен бота");
      return;
    }
    setBotLoading(true);
    setError("");
    try {
      const result = await telegramBotApi.setup(botToken.trim());
      setTelegramBot(result);
      setBotToken("");
      setSuccess("Telegram бот успешно подключен!");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ошибка подключения бота");
    } finally {
      setBotLoading(false);
    }
  };

  const handleDisableTelegramBot = async () => {
    if (!confirm("Отключить Telegram бота?")) return;
    setBotLoading(true);
    try {
      await telegramBotApi.disable();
      setTelegramBot({ enabled: false, bot_username: null, webhook_url: null });
      setSuccess("Telegram бот отключен");
    } catch {
      setError("Ошибка отключения бота");
    } finally {
      setBotLoading(false);
    }
  };

  const isAdmin =
    members.find((m) => m.user_id === Number(currentUser?.id))?.role === "admin" ||
    members.find((m) => m.user_id === Number(currentUser?.id))?.role === "owner";

  return (
    <Box
      sx={{
        width: "100vw",
        height: "100vh",
        backgroundColor: themeColors.bg.primary,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Mobile: TopBar */}
      {isMobile && (
        <TopBar
          onMenuClick={() => setMobileMenuOpen(true)}
          title="Настройки"
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
          display: "flex",
          flexDirection: "column",
          marginLeft: isDesktop ? "240px" : 0,
          height: isMobile ? "calc(100vh - 56px)" : "100vh",
          overflowY: "auto",
        }}
      >
        <Box
          sx={{
            maxWidth: "900px",
            width: "100%",
            margin: "0 auto",
            padding: isMobile ? "16px" : "32px 24px",
          }}
        >
          {loading ? (
            <Box sx={{ textAlign: "center", padding: "48px", color: themeColors.text.secondary }}>
              Загрузка...
            </Box>
          ) : !organization ? (
            <Box
              sx={{
                padding: "48px",
                textAlign: "center",
                backgroundColor: themeColors.bg.secondary,
                border: `1px solid ${themeColors.border.primary}`,
                borderRadius: "8px",
              }}
            >
              <Box sx={{ fontSize: "18px", fontWeight: 500, color: themeColors.text.primary, marginBottom: "8px" }}>
                Нет организации
              </Box>
              <Box sx={{ fontSize: "14px", color: themeColors.text.secondary }}>
                Создайте новую или присоединитесь по приглашению
              </Box>
            </Box>
          ) : (
            <>
              {/* Header */}
              <Box sx={{ marginBottom: "24px" }}>
                <Box sx={{ fontSize: isMobile ? "24px" : "28px", fontWeight: 600, color: themeColors.text.primary, marginBottom: "8px" }}>
                  {organization.name}
                </Box>
                <Box sx={{ fontSize: "14px", color: themeColors.text.secondary }}>
                  {stats?.total_members} участников • {stats?.total_documents} документов
                </Box>
              </Box>

              {/* Alerts */}
              {error && (
                <Box sx={{ padding: "12px 16px", backgroundColor: themeColors.accent.red, color: "#ffffff", borderRadius: "6px", fontSize: "14px", marginBottom: "16px" }}>
                  {error}
                </Box>
              )}
              {success && (
                <Box sx={{ padding: "12px 16px", backgroundColor: themeColors.accent.green, color: "#ffffff", borderRadius: "6px", fontSize: "14px", marginBottom: "16px" }}>
                  {success}
                </Box>
              )}

              {/* Tabs */}
              <Box sx={{ display: "flex", gap: "8px", marginBottom: "24px", borderBottom: `1px solid ${themeColors.border.primary}`, paddingBottom: "12px", flexWrap: "wrap" }}>
                <TabButton active={activeTab === "members"} onClick={() => setActiveTab("members")} themeColors={themeColors}>
                  <PeopleIcon size={16} /> Участники
                </TabButton>
                {isAdmin && (
                  <TabButton active={activeTab === "invites"} onClick={() => setActiveTab("invites")} themeColors={themeColors}>
                    <LinkIcon size={16} /> Приглашения
                  </TabButton>
                )}
                {isAdmin && (
                  <TabButton active={activeTab === "settings"} onClick={() => setActiveTab("settings")} themeColors={themeColors}>
                    <GearIcon size={16} /> Настройки AI
                  </TabButton>
                )}
                {isAdmin && (
                  <TabButton active={activeTab === "telegram"} onClick={() => setActiveTab("telegram")} themeColors={themeColors}>
                    🤖 Telegram
                  </TabButton>
                )}
              </Box>

              {/* Content */}
              <Box sx={{ backgroundColor: themeColors.bg.secondary, border: `1px solid ${themeColors.border.primary}`, borderRadius: "8px", padding: "24px" }}>
                {/* Members Tab */}
                {activeTab === "members" && (
                  <Box>
                    <Box sx={{ fontSize: "16px", fontWeight: 600, color: themeColors.text.primary, marginBottom: "16px" }}>
                      Участники организации
                    </Box>
                    <Box sx={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                      {members.map((member) => (
                        <Box key={member.user_id} sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", backgroundColor: themeColors.bg.tertiary, borderRadius: "6px" }}>
                          <Box>
                            <Box sx={{ fontWeight: 500, color: themeColors.text.primary }}>{member.full_name || member.email}</Box>
                            <Box sx={{ fontSize: "12px", color: themeColors.text.secondary }}>{member.email}</Box>
                          </Box>
                          <Box sx={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <Box sx={{ padding: "4px 8px", fontSize: "12px", borderRadius: "4px", backgroundColor: member.role === "owner" ? themeColors.accent.blue : themeColors.bg.primary, color: themeColors.text.primary }}>
                              {member.role === "owner" ? "Владелец" : member.role === "admin" ? "Админ" : "Участник"}
                            </Box>
                            {isAdmin && member.role !== "owner" && member.user_id !== Number(currentUser?.id) && (
                              <Box as="button" onClick={() => handleRemoveMember(member.user_id)} sx={{ padding: "6px", backgroundColor: "transparent", border: `1px solid ${themeColors.border.primary}`, borderRadius: "6px", cursor: "pointer", color: themeColors.text.secondary, "&:hover": { backgroundColor: themeColors.accent.red, borderColor: themeColors.accent.red, color: "#ffffff" } }}>
                                <TrashIcon size={14} />
                              </Box>
                            )}
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Invites Tab */}
                {activeTab === "invites" && isAdmin && (
                  <Box>
                    <Box sx={{ fontSize: "16px", fontWeight: 600, color: themeColors.text.primary, marginBottom: "16px" }}>
                      Создать приглашение
                    </Box>
                    <Box sx={{ display: "flex", gap: "12px", marginBottom: "24px", flexWrap: "wrap", alignItems: "flex-end" }}>
                      <Box>
                        <Box sx={{ fontSize: "12px", color: themeColors.text.secondary, marginBottom: "4px" }}>Макс. использований</Box>
                        <Box as="input" type="number" value={inviteMaxUses} onChange={(e: any) => setInviteMaxUses(Number(e.target.value))} sx={{ width: "100px", padding: "8px 12px", borderRadius: "6px", border: `1px solid ${themeColors.border.primary}`, backgroundColor: themeColors.bg.primary, color: themeColors.text.primary, fontSize: "14px" }} />
                      </Box>
                      <Box>
                        <Box sx={{ fontSize: "12px", color: themeColors.text.secondary, marginBottom: "4px" }}>Срок (дней)</Box>
                        <Box as="input" type="number" value={inviteExpiresDays} onChange={(e: any) => setInviteExpiresDays(Number(e.target.value))} sx={{ width: "100px", padding: "8px 12px", borderRadius: "6px", border: `1px solid ${themeColors.border.primary}`, backgroundColor: themeColors.bg.primary, color: themeColors.text.primary, fontSize: "14px" }} />
                      </Box>
                      <Box as="button" onClick={handleCreateInvite} sx={{ padding: "8px 16px", background: themeColors.accent.blueGradient, color: "#ffffff", border: "none", borderRadius: "6px", fontSize: "14px", fontWeight: 500, cursor: "pointer", "&:hover": { opacity: 0.9 } }}>
                        Создать
                      </Box>
                    </Box>
                    <Box sx={{ fontSize: "16px", fontWeight: 600, color: themeColors.text.primary, marginBottom: "16px" }}>
                      Активные приглашения
                    </Box>
                    {invites.length === 0 ? (
                      <Box sx={{ color: themeColors.text.secondary, fontSize: "14px" }}>Нет активных приглашений</Box>
                    ) : (
                      <Box sx={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                        {invites.map((invite) => (
                          <Box key={invite.id} sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", backgroundColor: themeColors.bg.tertiary, borderRadius: "6px" }}>
                            <Box>
                              <Box sx={{ fontFamily: "monospace", fontSize: "14px", color: themeColors.text.primary }}>{invite.code.substring(0, 12)}...</Box>
                              <Box sx={{ fontSize: "12px", color: themeColors.text.secondary }}>Использовано: {invite.used_count}/{invite.max_uses}</Box>
                            </Box>
                            <Box sx={{ display: "flex", gap: "8px" }}>
                              <Box as="button" onClick={() => handleCopyInviteLink(invite.code)} sx={{ padding: "6px 12px", backgroundColor: themeColors.bg.primary, border: `1px solid ${themeColors.border.primary}`, borderRadius: "6px", fontSize: "12px", cursor: "pointer", color: themeColors.text.primary, display: "flex", alignItems: "center", gap: "4px", "&:hover": { borderColor: themeColors.accent.blue } }}>
                                {copiedCode === invite.code ? <CheckIcon size={14} /> : <CopyIcon size={14} />}
                                {copiedCode === invite.code ? "Скопировано" : "Копировать"}
                              </Box>
                              <Box as="button" onClick={() => handleRevokeInvite(invite.id)} sx={{ padding: "6px 12px", backgroundColor: "transparent", border: `1px solid ${themeColors.accent.red}`, borderRadius: "6px", fontSize: "12px", cursor: "pointer", color: themeColors.accent.red, "&:hover": { backgroundColor: themeColors.accent.red, color: "#ffffff" } }}>
                                Отозвать
                              </Box>
                            </Box>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </Box>
                )}

                {/* Settings Tab */}
                {activeTab === "settings" && isAdmin && (
                  <Box>
                    <Box sx={{ fontSize: "16px", fontWeight: 600, color: themeColors.text.primary, marginBottom: "16px" }}>
                      Настройки AI
                    </Box>
                    <Box sx={{ marginBottom: "20px" }}>
                      <Box sx={{ fontSize: "14px", color: themeColors.text.primary, marginBottom: "8px" }}>Системный промпт</Box>
                      <Box as="textarea" value={settingsForm.custom_system_prompt} onChange={(e: any) => setSettingsForm({ ...settingsForm, custom_system_prompt: e.target.value })} placeholder="Введите инструкции для AI..." rows={6} sx={{ width: "100%", padding: "12px", borderRadius: "6px", border: `1px solid ${themeColors.border.primary}`, backgroundColor: themeColors.bg.primary, color: themeColors.text.primary, fontSize: "14px", resize: "vertical" }} />
                      <Box sx={{ fontSize: "12px", color: themeColors.text.secondary, marginTop: "4px" }}>Специальные инструкции для AI при ответах</Box>
                    </Box>
                    <Box sx={{ marginBottom: "20px" }}>
                      <Box sx={{ fontSize: "14px", color: themeColors.text.primary, marginBottom: "8px" }}>Temperature ({settingsForm.custom_temperature})</Box>
                      <Box as="input" type="range" min="0" max="2" step="0.1" value={settingsForm.custom_temperature} onChange={(e: any) => setSettingsForm({ ...settingsForm, custom_temperature: Number(e.target.value) })} sx={{ width: "100%", maxWidth: "300px" }} />
                      <Box sx={{ fontSize: "12px", color: themeColors.text.secondary, marginTop: "4px" }}>Низкая = точные ответы, высокая = креативные</Box>
                    </Box>
                    <Box as="button" onClick={handleSaveSettings} sx={{ padding: "10px 20px", background: themeColors.accent.blueGradient, color: "#ffffff", border: "none", borderRadius: "6px", fontSize: "14px", fontWeight: 500, cursor: "pointer", "&:hover": { opacity: 0.9 } }}>
                      Сохранить настройки
                    </Box>
                  </Box>
                )}

                {/* Telegram Tab */}
                {activeTab === "telegram" && isAdmin && (
                  <Box>
                    <Box sx={{ fontSize: "16px", fontWeight: 600, color: themeColors.text.primary, marginBottom: "16px" }}>
                      🤖 Telegram Бот
                    </Box>
                    {telegramBot.enabled ? (
                      <>
                        <Box sx={{ padding: "16px", backgroundColor: theme === "dark" ? "#1a3d2e" : "#dafbe1", border: `1px solid ${themeColors.accent.green}`, borderRadius: "6px", marginBottom: "20px" }}>
                          <Box sx={{ fontWeight: 600, color: themeColors.accent.green, marginBottom: "4px" }}>✅ Бот активен</Box>
                          <Box sx={{ color: themeColors.accent.green }}>@{telegramBot.bot_username}</Box>
                        </Box>
                        <Box sx={{ marginBottom: "20px" }}>
                          <Box sx={{ fontWeight: 500, color: themeColors.text.primary, marginBottom: "8px" }}>Как использовать:</Box>
                          <Box as="ol" sx={{ margin: 0, paddingLeft: "20px", color: themeColors.text.secondary, fontSize: "14px", lineHeight: 1.6 }}>
                            <li>Найдите бота: @{telegramBot.bot_username}</li>
                            <li>Нажмите Start или /start</li>
                            <li>Задавайте вопросы</li>
                          </Box>
                        </Box>
                        <Box as="button" onClick={handleDisableTelegramBot} disabled={botLoading} sx={{ padding: "10px 20px", backgroundColor: "transparent", border: `1px solid ${themeColors.accent.red}`, color: themeColors.accent.red, borderRadius: "6px", fontSize: "14px", fontWeight: 500, cursor: botLoading ? "wait" : "pointer", "&:hover": { backgroundColor: themeColors.accent.red, color: "#ffffff" } }}>
                          {botLoading ? "Отключение..." : "Отключить бота"}
                        </Box>
                      </>
                    ) : (
                      <>
                        <Box sx={{ padding: "16px", backgroundColor: theme === "dark" ? "#3d2e1a" : "#fff8c5", border: `1px solid ${themeColors.accent.orange}`, borderRadius: "6px", marginBottom: "20px" }}>
                          <Box sx={{ fontWeight: 600, color: themeColors.accent.orange, marginBottom: "4px" }}>Бот не подключен</Box>
                          <Box sx={{ fontSize: "14px", color: themeColors.accent.orange }}>Подключите бота для доступа через Telegram</Box>
                        </Box>
                        <Box sx={{ marginBottom: "20px" }}>
                          <Box sx={{ fontWeight: 500, color: themeColors.text.primary, marginBottom: "8px" }}>Как создать бота:</Box>
                          <Box as="ol" sx={{ margin: 0, paddingLeft: "20px", color: themeColors.text.secondary, fontSize: "14px", lineHeight: 1.6 }}>
                            <li>Откройте @BotFather в Telegram</li>
                            <li>Отправьте /newbot</li>
                            <li>Скопируйте токен</li>
                            <li>Вставьте ниже</li>
                          </Box>
                        </Box>
                        <Box sx={{ marginBottom: "16px" }}>
                          <Box sx={{ fontSize: "14px", color: themeColors.text.primary, marginBottom: "8px" }}>Токен бота</Box>
                          <Box as="input" type="password" value={botToken} onChange={(e: any) => setBotToken(e.target.value)} placeholder="123456789:ABCdef..." sx={{ width: "100%", maxWidth: "400px", padding: "10px 12px", borderRadius: "6px", border: `1px solid ${themeColors.border.primary}`, backgroundColor: themeColors.bg.primary, color: themeColors.text.primary, fontSize: "14px" }} />
                        </Box>
                        <Box as="button" onClick={handleSetupTelegramBot} disabled={botLoading || !botToken.trim()} sx={{ padding: "10px 20px", background: botLoading || !botToken.trim() ? themeColors.bg.tertiary : themeColors.accent.blueGradient, color: "#ffffff", border: "none", borderRadius: "6px", fontSize: "14px", fontWeight: 500, cursor: botLoading || !botToken.trim() ? "not-allowed" : "pointer", opacity: botLoading || !botToken.trim() ? 0.6 : 1 }}>
                          {botLoading ? "Подключение..." : "Подключить бота"}
                        </Box>
                      </>
                    )}
                  </Box>
                )}
              </Box>
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
}

// Tab button component
function TabButton({ active, onClick, children, themeColors }: { active: boolean; onClick: () => void; children: React.ReactNode; themeColors: any }) {
  return (
    <Box
      as="button"
      onClick={onClick}
      sx={{
        display: "flex",
        alignItems: "center",
        gap: "6px",
        padding: "8px 12px",
        backgroundColor: active ? themeColors.accent.blue : "transparent",
        color: active ? "#ffffff" : themeColors.text.secondary,
        border: "none",
        borderRadius: "6px",
        fontSize: "14px",
        fontWeight: 500,
        cursor: "pointer",
        "&:hover": {
          backgroundColor: active ? themeColors.accent.blue : themeColors.bg.tertiary,
        },
      }}
    >
      {children}
    </Box>
  );
}
