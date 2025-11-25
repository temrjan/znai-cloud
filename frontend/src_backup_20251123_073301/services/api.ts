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

  upload: async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post<Document>("/documents/upload", formData, {
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
  query: async (question: string): Promise<{ answer: string; sources: string[] }> => {
    const response = await api.post<{ answer: string; sources: string[] }>("/chat", {
      question,
    });
    return response.data;
  },
};

export const adminApi = {
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
};
