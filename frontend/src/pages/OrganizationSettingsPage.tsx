/**
 * Organization settings page with members, invites, and AI settings
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Flash,
  Heading,
  Text,
  TextInput,
  FormControl,
  Textarea,
  Spinner,
  Label,
} from "@primer/react";
import {
  PeopleIcon,
  GearIcon,
  LinkIcon,
  TrashIcon,
  CopyIcon,
  CheckIcon,
} from "@primer/octicons-react";
import { organizationsApi, authApi } from "../services/api";
import type {
  Organization,
  OrganizationMember,
  OrganizationInvite,
  OrganizationStats,
} from "../types";

type TabType = "members" | "invites" | "settings";

export function OrganizationSettingsPage() {
  const navigate = useNavigate();
  const currentUser = authApi.getCurrentUser();

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
    custom_max_tokens: 2500,
    response_language: "ru",
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [org, membersData, invitesData, settingsData, statsData] =
        await Promise.all([
          organizationsApi.getMyOrganization(),
          organizationsApi.getMembers(),
          organizationsApi.getInvites().catch(() => []),
          organizationsApi.getSettings(),
          organizationsApi.getStats(),
        ]);

      setOrganization(org);
      setMembers(membersData);
      setInvites(invitesData);
      setStats(statsData);

      setSettingsForm({
        custom_system_prompt: settingsData.custom_system_prompt || "",
        custom_temperature: settingsData.custom_temperature || 0.7,
        custom_max_tokens: settingsData.custom_max_tokens || 2500,
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

  const isAdmin =
    members.find((m) => m.user_id === Number(currentUser?.id))?.role === "admin" ||
    members.find((m) => m.user_id === Number(currentUser?.id))?.role === "owner";

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Spinner size="large" />
      </div>
    );
  }

  if (!organization) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#f6f8fa",
          padding: "1rem",
        }}
      >
        <div
          style={{
            maxWidth: "400px",
            backgroundColor: "white",
            borderRadius: "6px",
            border: "1px solid #d0d7de",
            padding: "2rem",
            textAlign: "center",
          }}
        >
          <Heading as="h2" style={{ marginBottom: "1rem" }}>
            Нет организации
          </Heading>
          <Text as="p" style={{ color: "#57606a", marginBottom: "1.5rem" }}>
            Вы не состоите в организации. Создайте новую или присоединитесь по
            приглашению.
          </Text>
          <Button onClick={() => navigate("/chat")} variant="primary">
            Вернуться
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f6f8fa",
        padding: "1rem",
      }}
    >
      <div style={{ maxWidth: "900px", margin: "0 auto" }}>
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.5rem",
          }}
        >
          <div>
            <Heading as="h1" style={{ fontSize: "1.5rem" }}>
              {organization.name}
            </Heading>
            <Text as="p" style={{ color: "#57606a" }}>
              {stats?.total_members} участников • {stats?.total_documents}{" "}
              документов
            </Text>
          </div>
          <Button onClick={() => navigate("/chat")}>Назад к чату</Button>
        </div>

        {/* Alerts */}
        {error && (
          <Flash variant="danger" style={{ marginBottom: "1rem" }}>
            {error}
          </Flash>
        )}
        {success && (
          <Flash variant="success" style={{ marginBottom: "1rem" }}>
            {success}
          </Flash>
        )}

        {/* Tabs */}
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            marginBottom: "1.5rem",
            borderBottom: "1px solid #d0d7de",
            paddingBottom: "0.5rem",
          }}
        >
          <Button
            variant={activeTab === "members" ? "primary" : "invisible"}
            onClick={() => setActiveTab("members")}
            leadingVisual={PeopleIcon}
          >
            Участники
          </Button>
          {isAdmin && (
            <Button
              variant={activeTab === "invites" ? "primary" : "invisible"}
              onClick={() => setActiveTab("invites")}
              leadingVisual={LinkIcon}
            >
              Приглашения
            </Button>
          )}
          {isAdmin && (
            <Button
              variant={activeTab === "settings" ? "primary" : "invisible"}
              onClick={() => setActiveTab("settings")}
              leadingVisual={GearIcon}
            >
              Настройки AI
            </Button>
          )}
        </div>

        {/* Content */}
        <div
          style={{
            backgroundColor: "white",
            borderRadius: "6px",
            border: "1px solid #d0d7de",
            padding: "1.5rem",
          }}
        >
          {/* Members Tab */}
          {activeTab === "members" && (
            <div>
              <Heading as="h3" style={{ fontSize: "1rem", marginBottom: "1rem" }}>
                Участники организации
              </Heading>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                {members.map((member) => (
                  <div
                    key={member.user_id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "0.75rem",
                      backgroundColor: "#f6f8fa",
                      borderRadius: "6px",
                    }}
                  >
                    <div>
                      <Text as="p" style={{ fontWeight: 600 }}>
                        {member.full_name || member.email}
                      </Text>
                      <Text as="p" style={{ fontSize: "0.875rem", color: "#57606a" }}>
                        {member.email}
                      </Text>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <Label
                        variant={member.role === "owner" ? "accent" : "secondary"}
                      >
                        {member.role === "owner"
                          ? "Владелец"
                          : member.role === "admin"
                          ? "Админ"
                          : "Участник"}
                      </Label>
                      {isAdmin &&
                        member.role !== "owner" &&
                        member.user_id !== Number(currentUser?.id) && (
                          <Button
                            variant="danger"
                            size="small"
                            onClick={() => handleRemoveMember(member.user_id)}
                          >
                            <TrashIcon />
                          </Button>
                        )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Invites Tab */}
          {activeTab === "invites" && isAdmin && (
            <div>
              <Heading as="h3" style={{ fontSize: "1rem", marginBottom: "1rem" }}>
                Создать приглашение
              </Heading>
              <div
                style={{
                  display: "flex",
                  gap: "1rem",
                  marginBottom: "1.5rem",
                  flexWrap: "wrap",
                }}
              >
                <FormControl>
                  <FormControl.Label>Макс. использований</FormControl.Label>
                  <TextInput
                    type="number"
                    value={inviteMaxUses}
                    onChange={(e) => setInviteMaxUses(Number(e.target.value))}
                    min={1}
                    max={100}
                    style={{ width: "120px" }}
                  />
                </FormControl>
                <FormControl>
                  <FormControl.Label>Срок действия (дней)</FormControl.Label>
                  <TextInput
                    type="number"
                    value={inviteExpiresDays}
                    onChange={(e) => setInviteExpiresDays(Number(e.target.value))}
                    min={1}
                    max={365}
                    style={{ width: "120px" }}
                  />
                </FormControl>
                <div style={{ display: "flex", alignItems: "flex-end" }}>
                  <Button variant="primary" onClick={handleCreateInvite}>
                    Создать
                  </Button>
                </div>
              </div>

              <Heading as="h3" style={{ fontSize: "1rem", marginBottom: "1rem" }}>
                Активные приглашения
              </Heading>
              {invites.length === 0 ? (
                <Text as="p" style={{ color: "#57606a" }}>
                  Нет активных приглашений
                </Text>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {invites.map((invite) => (
                    <div
                      key={invite.id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "0.75rem",
                        backgroundColor: "#f6f8fa",
                        borderRadius: "6px",
                      }}
                    >
                      <div>
                        <code style={{ fontSize: "0.875rem" }}>
                          {invite.code.substring(0, 8)}...
                        </code>
                        <Text
                          as="p"
                          style={{ fontSize: "0.75rem", color: "#57606a" }}
                        >
                          Использовано: {invite.used_count}/{invite.max_uses}
                        </Text>
                      </div>
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        <Button
                          size="small"
                          onClick={() => handleCopyInviteLink(invite.code)}
                          leadingVisual={
                            copiedCode === invite.code ? CheckIcon : CopyIcon
                          }
                        >
                          {copiedCode === invite.code ? "Скопировано" : "Копировать"}
                        </Button>
                        <Button
                          variant="danger"
                          size="small"
                          onClick={() => handleRevokeInvite(invite.id)}
                        >
                          Отозвать
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === "settings" && isAdmin && (
            <div>
              <Heading as="h3" style={{ fontSize: "1rem", marginBottom: "1rem" }}>
                Настройки AI
              </Heading>

              <FormControl style={{ marginBottom: "1rem" }}>
                <FormControl.Label>Системный промпт</FormControl.Label>
                <Textarea
                  value={settingsForm.custom_system_prompt}
                  onChange={(e) =>
                    setSettingsForm({
                      ...settingsForm,
                      custom_system_prompt: e.target.value,
                    })
                  }
                  placeholder="Введите кастомные инструкции для AI..."
                  rows={6}
                  block
                />
                <FormControl.Caption>
                  Специальные инструкции для AI при ответах на вопросы
                </FormControl.Caption>
              </FormControl>

              <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
                <FormControl style={{ flex: 1 }}>
                  <FormControl.Label>Temperature ({settingsForm.custom_temperature})</FormControl.Label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={settingsForm.custom_temperature}
                    onChange={(e) =>
                      setSettingsForm({
                        ...settingsForm,
                        custom_temperature: Number(e.target.value),
                      })
                    }
                    style={{ width: "100%" }}
                  />
                  <FormControl.Caption>
                    Низкая = точные ответы, высокая = креативные
                  </FormControl.Caption>
                </FormControl>

                <FormControl style={{ flex: 1 }}>
                  <FormControl.Label>Max Tokens</FormControl.Label>
                  <TextInput
                    type="number"
                    value={settingsForm.custom_max_tokens}
                    onChange={(e) =>
                      setSettingsForm({
                        ...settingsForm,
                        custom_max_tokens: Number(e.target.value),
                      })
                    }
                    min={100}
                    max={8000}
                  />
                  <FormControl.Caption>
                    Максимальная длина ответа
                  </FormControl.Caption>
                </FormControl>
              </div>

              <FormControl style={{ marginBottom: "1.5rem" }}>
                <FormControl.Label>Язык ответов</FormControl.Label>
                <select
                  value={settingsForm.response_language}
                  onChange={(e) =>
                    setSettingsForm({
                      ...settingsForm,
                      response_language: e.target.value,
                    })
                  }
                  style={{
                    padding: "0.5rem",
                    borderRadius: "6px",
                    border: "1px solid #d0d7de",
                  }}
                >
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                  <option value="ar">العربية</option>
                </select>
              </FormControl>

              <Button variant="primary" onClick={handleSaveSettings}>
                Сохранить настройки
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
