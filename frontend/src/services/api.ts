/**
 * API client for backend communication
 */
import axios, { AxiosError } from "axios";
import type {
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  User,
  Document,
  UserQuota,
  HealthCheck,
  Organization,
  OrganizationMember,
  OrganizationInvite,
  OrganizationSettings,
  OrganizationStats,
  PendingOrganization,
  AdminStats,
} from "../types";

const API_BASE_URL = "/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>("/auth/register", data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>("/auth/login", data);
    const { access_token, user } = response.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("user", JSON.stringify(user));
    return response.data;
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  },

  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem("access_token");
  },
};

export const healthApi = {
  check: async (): Promise<HealthCheck> => {
    const response = await api.get<HealthCheck>("/health");
    return response.data;
  },
};

export const documentsApi = {
  list: async (): Promise<Document[]> => {
    const response = await api.get<Document[]>("/documents");
    return response.data;
  },

  upload: async (file: File, visibility: "private" | "organization" = "private"): Promise<Document> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post<Document>(`/documents/upload?visibility=${visibility}`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  index: async (id: string): Promise<Document> => {
    const response = await api.post<Document>(`/documents/${id}/index`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },
};

export const quotaApi = {
  get: async (): Promise<UserQuota> => {
    const response = await api.get<UserQuota>("/quota");
    return response.data;
  },
};

export const chatApi = {
  query: async (
    question: string,
    searchScope: "all" | "organization" | "private" = "all",
    sessionId?: number
  ): Promise<{ answer: string; sources: string[]; session_id: number }> => {
    const response = await api.post<{ answer: string; sources: string[]; session_id: number }>("/chat", {
      question,
      search_scope: searchScope,
      session_id: sessionId,
    });
    return response.data;
  },
};

export const chatSessionsApi = {
  list: async (): Promise<import('../types').ChatSessionListResponse> => {
    const response = await api.get<import('../types').ChatSessionListResponse>("/chat-sessions");
    return response.data;
  },

  get: async (sessionId: number): Promise<import('../types').ChatSessionWithMessages> => {
    const response = await api.get<import('../types').ChatSessionWithMessages>(`/chat-sessions/${sessionId}`);
    return response.data;
  },

  create: async (title?: string): Promise<import('../types').ChatSession> => {
    const response = await api.post<import('../types').ChatSession>("/chat-sessions", { title });
    return response.data;
  },

  update: async (sessionId: number, title: string): Promise<import('../types').ChatSession> => {
    const response = await api.patch<import('../types').ChatSession>(`/chat-sessions/${sessionId}`, { title });
    return response.data;
  },

  delete: async (sessionId: number): Promise<void> => {
    await api.delete(`/chat-sessions/${sessionId}`);
  },
};

export const adminApi = {
  // Stats
  getStats: async (): Promise<AdminStats> => {
    const response = await api.get<AdminStats>("/admin/stats");
    return response.data;
  },

  // Users
  getPendingUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>("/admin/users/pending");
    return response.data;
  },

  approveUser: async (userId: string): Promise<User> => {
    const response = await api.post<User>(`/admin/users/${userId}/approve`);
    return response.data;
  },

  rejectUser: async (userId: string): Promise<User> => {
    const response = await api.post<User>(`/admin/users/${userId}/reject`);
    return response.data;
  },

  // Organizations
  getPendingOrganizations: async (): Promise<PendingOrganization[]> => {
    const response = await api.get<PendingOrganization[]>("/admin/organizations/pending");
    return response.data;
  },

  approveOrganization: async (orgId: number): Promise<PendingOrganization> => {
    const response = await api.post<PendingOrganization>(`/admin/organizations/${orgId}/approve`);
    return response.data;
  },

  rejectOrganization: async (orgId: number): Promise<void> => {
    await api.post(`/admin/organizations/${orgId}/reject`);
  },
};

export const organizationsApi = {
  // Organization info
  getMyOrganization: async (): Promise<Organization> => {
    const response = await api.get<Organization>("/organizations/my");
    return response.data;
  },

  // Members
  getMembers: async (): Promise<OrganizationMember[]> => {
    const response = await api.get<OrganizationMember[]>("/organizations/my/members");
    return response.data;
  },

  removeMember: async (userId: number): Promise<void> => {
    await api.delete(`/organizations/my/members/${userId}`);
  },

  // Invites
  getInvites: async (): Promise<OrganizationInvite[]> => {
    const response = await api.get<OrganizationInvite[]>("/organizations/my/invites");
    return response.data;
  },

  createInvite: async (data: {
    max_uses?: number;
    expires_in_days?: number;
    default_role?: string;
  }): Promise<OrganizationInvite> => {
    const response = await api.post<OrganizationInvite>("/organizations/my/invites", data);
    return response.data;
  },

  revokeInvite: async (inviteId: number): Promise<void> => {
    await api.delete(`/organizations/my/invites/${inviteId}`);
  },

  // Settings
  getSettings: async (): Promise<OrganizationSettings> => {
    const response = await api.get<OrganizationSettings>("/organizations/my/settings");
    return response.data;
  },

  updateSettings: async (data: Partial<OrganizationSettings>): Promise<OrganizationSettings> => {
    const response = await api.patch<OrganizationSettings>("/organizations/my/settings", data);
    return response.data;
  },

  // Stats
  getStats: async (): Promise<OrganizationStats> => {
    const response = await api.get<OrganizationStats>("/organizations/my/stats");
    return response.data;
  },

  // Public invite details (no auth required)
  getInviteDetails: async (code: string): Promise<import('../types').InviteDetails> => {
    const response = await api.get<import('../types').InviteDetails>(`/organizations/invites/${code}`);
    return response.data;
  },
};

// Telegram Bot
export const telegramBotApi = {
  getStatus: async (): Promise<{ enabled: boolean; bot_username: string | null; webhook_url: string | null }> => {
    const response = await api.get<{ enabled: boolean; bot_username: string | null; webhook_url: string | null }>("/organizations/my/telegram-bot");
    return response.data;
  },

  setup: async (botToken: string): Promise<{ enabled: boolean; bot_username: string | null; webhook_url: string | null }> => {
    const response = await api.post<{ enabled: boolean; bot_username: string | null; webhook_url: string | null }>("/organizations/my/telegram-bot", {
      bot_token: botToken
    });
    return response.data;
  },

  disable: async (): Promise<void> => {
    await api.delete("/organizations/my/telegram-bot");
  },
};
