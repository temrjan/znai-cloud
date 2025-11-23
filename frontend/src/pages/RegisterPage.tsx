/**
 * Registration page with organization support
 */
import { useState, useEffect } from "react";
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import {
  Button,
  FormControl,
  TextInput,
  Flash,
  Heading,
  Text,
  SegmentedControl,
} from "@primer/react";
import { OrganizationIcon, PersonIcon, LinkIcon } from "@primer/octicons-react";
import { authApi, organizationsApi } from "../services/api";
import type { InviteDetails } from "../types";

type RegistrationMode = "personal" | "organization" | "invite";

export function RegisterPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inviteCode = searchParams.get("invite");

  const [mode, setMode] = useState<RegistrationMode>(
    inviteCode ? "invite" : "personal"
  );
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
    organization_name: "",
    invite_code: inviteCode || "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [autoApproved, setAutoApproved] = useState(false);
  const [inviteDetails, setInviteDetails] = useState<InviteDetails | null>(null);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteError, setInviteError] = useState("");

  // Load invite details when code changes
  useEffect(() => {
    if (inviteCode) {
      setMode("invite");
      setFormData((prev) => ({ ...prev, invite_code: inviteCode }));
      loadInviteDetails(inviteCode);
    }
  }, [inviteCode]);

  const loadInviteDetails = async (code: string) => {
    setInviteLoading(true);
    setInviteError("");
    try {
      const details = await organizationsApi.getInviteDetails(code);
      setInviteDetails(details);
      if (!details.is_valid) {
        setInviteError("Приглашение недействительно или истекло");
      }
    } catch (err: any) {
      setInviteError(err.response?.data?.detail || "Не удалось загрузить информацию о приглашении");
      setInviteDetails(null);
    } finally {
      setInviteLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Пароли не совпадают");
      return;
    }

    if (formData.password.length < 8) {
      setError("Пароль должен быть минимум 8 символов");
      return;
    }

    if (mode === "organization" && !formData.organization_name.trim()) {
      setError("Введите название организации");
      return;
    }

    if (mode === "invite" && !formData.invite_code.trim()) {
      setError("Введите код приглашения");
      return;
    }

    setLoading(true);

    try {
      const requestData: Record<string, string> = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      };

      if (mode === "organization") {
        requestData.organization_name = formData.organization_name;
      } else if (mode === "invite") {
        requestData.invite_code = formData.invite_code;
      }

      await authApi.register(requestData as any);
      setAutoApproved(mode === "organization" || mode === "invite");
      setSuccess(true);
    } catch (err: any) {
      const message =
        err.response?.data?.detail || "Ошибка регистрации. Попробуйте снова.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
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
            width: "100%",
            maxWidth: "400px",
            backgroundColor: "white",
            borderRadius: "6px",
            border: "1px solid #d0d7de",
            padding: "2rem",
            textAlign: "center",
          }}
        >
          <Flash variant="success" style={{ marginBottom: "1rem" }}>
            Регистрация успешна!
          </Flash>
          <Heading
            as="h2"
            style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}
          >
            {autoApproved ? "Добро пожаловать!" : "Ожидание одобрения"}
          </Heading>
          <Text as="p" style={{ color: "#57606a", marginBottom: "1.5rem" }}>
            {autoApproved
              ? "Ваш аккаунт активирован. Теперь вы можете войти."
              : "Ваш аккаунт создан и ожидает одобрения администратора."}
          </Text>
          <Button
            onClick={() => navigate("/login")}
            variant="primary"
            size="large"
          >
            Войти
          </Button>
        </div>
      </div>
    );
  }

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
      <form
        onSubmit={handleSubmit}
        style={{
          width: "100%",
          maxWidth: "440px",
          backgroundColor: "white",
          borderRadius: "6px",
          border: "1px solid #d0d7de",
          padding: "2rem",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <Heading
            as="h1"
            style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}
          >
            Создать аккаунт
          </Heading>
          <Text as="p" style={{ color: "#57606a" }}>
            Znai.cloud — база знаний с AI
          </Text>
        </div>

        {/* Registration mode selector */}
        <div style={{ marginBottom: "1rem" }}>
          <SegmentedControl
            aria-label="Тип регистрации"
            fullWidth
            onChange={(index) => {
              const modes: RegistrationMode[] = [
                "personal",
                "organization",
                "invite",
              ];
              setMode(modes[index]);
              setError("");
            }}
          >
            <SegmentedControl.Button
              selected={mode === "personal"}
              leadingVisual={PersonIcon}
            >
              Личный
            </SegmentedControl.Button>
            <SegmentedControl.Button
              selected={mode === "organization"}
              leadingVisual={OrganizationIcon}
            >
              Организация
            </SegmentedControl.Button>
            <SegmentedControl.Button
              selected={mode === "invite"}
              leadingVisual={LinkIcon}
            >
              По инвайту
            </SegmentedControl.Button>
          </SegmentedControl>
        </div>

        {/* Mode description */}
        <Flash
          variant={mode === "personal" ? "warning" : "default"}
          style={{ marginBottom: "1rem", fontSize: "0.875rem" }}
        >
          {mode === "personal" && (
            <>
              <strong>Личный аккаунт:</strong> Требуется одобрение
              администратора
            </>
          )}
          {mode === "organization" && (
            <>
              <strong>Создание организации:</strong> Вы станете владельцем и
              сможете приглашать участников
            </>
          )}
          {mode === "invite" && (
            <>
              <strong>По приглашению:</strong>{" "}
              {inviteLoading ? (
                "Загрузка..."
              ) : inviteDetails ? (
                <>
                  Вы присоединитесь к организации <strong>{inviteDetails.organization_name}</strong>
                </>
              ) : (
                "Присоединитесь к существующей организации"
              )}
            </>
          )}
        </Flash>

        {/* Invite error */}
        {mode === "invite" && inviteError && (
          <Flash variant="danger" style={{ marginBottom: "1rem" }}>
            {inviteError}
          </Flash>
        )}

        {error && (
          <Flash variant="danger" style={{ marginBottom: "1rem" }}>
            {error}
          </Flash>
        )}

        <FormControl required style={{ marginBottom: "1rem" }}>
          <FormControl.Label>Полное имя</FormControl.Label>
          <TextInput
            value={formData.full_name}
            onChange={(e) => handleChange("full_name", e.target.value)}
            placeholder="Иван Иванов"
            size="large"
            block
            disabled={loading}
          />
        </FormControl>

        <FormControl required style={{ marginBottom: "1rem" }}>
          <FormControl.Label>Email</FormControl.Label>
          <TextInput
            type="email"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            placeholder="your@email.com"
            size="large"
            block
            disabled={loading}
          />
        </FormControl>

        {/* Organization name field */}
        {mode === "organization" && (
          <FormControl required style={{ marginBottom: "1rem" }}>
            <FormControl.Label>Название организации</FormControl.Label>
            <TextInput
              value={formData.organization_name}
              onChange={(e) => handleChange("organization_name", e.target.value)}
              placeholder="Моя компания"
              size="large"
              block
              disabled={loading}
            />
            <FormControl.Caption>
              Будет использоваться для идентификации вашей команды
            </FormControl.Caption>
          </FormControl>
        )}

        {/* Invite code field */}
        {mode === "invite" && (
          <FormControl required style={{ marginBottom: "1rem" }}>
            <FormControl.Label>Код приглашения</FormControl.Label>
            <TextInput
              value={formData.invite_code}
              onChange={(e) => handleChange("invite_code", e.target.value)}
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              size="large"
              block
              disabled={loading}
              monospace
            />
            <FormControl.Caption>
              Получите код от администратора организации
            </FormControl.Caption>
          </FormControl>
        )}

        <FormControl required style={{ marginBottom: "1rem" }}>
          <FormControl.Label>Пароль</FormControl.Label>
          <TextInput
            type="password"
            value={formData.password}
            onChange={(e) => handleChange("password", e.target.value)}
            placeholder="Минимум 8 символов"
            size="large"
            block
            disabled={loading}
          />
        </FormControl>

        <FormControl required style={{ marginBottom: "1.5rem" }}>
          <FormControl.Label>Подтвердите пароль</FormControl.Label>
          <TextInput
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => handleChange("confirmPassword", e.target.value)}
            placeholder="Повторите пароль"
            size="large"
            block
            disabled={loading}
          />
        </FormControl>

        <Button
          type="submit"
          variant="primary"
          size="large"
          block
          disabled={loading}
          style={{ marginBottom: "1rem" }}
        >
          {loading ? "Создание аккаунта..." : "Создать аккаунт"}
        </Button>

        <Text
          as="p"
          style={{ textAlign: "center", fontSize: "0.875rem", color: "#57606a" }}
        >
          Уже есть аккаунт?{" "}
          <Link to="/login" style={{ color: "#0969da" }}>
            Войти
          </Link>
        </Text>
      </form>
    </div>
  );
}
