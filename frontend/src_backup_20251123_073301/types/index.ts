/**
 * Type definitions for AI-Avangard application
 */

export enum UserStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  SUSPENDED = "suspended",
}

export enum UserRole {
  USER = "user",
  ADMIN = "admin",
}

export enum DocumentStatus {
  PROCESSING = "processing",  // Uploaded, waiting for indexing
  INDEXING = "indexing",      // Currently being indexed
  INDEXED = "indexed",        // Successfully indexed
  FAILED = "failed",          // Indexing failed
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
}

export interface UserQuota {
  max_documents: number;
  current_documents: number;
  max_queries_daily: number;
  queries_used_today: number;
}

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  file_size: number;
  status: DocumentStatus;
  error_message?: string;
  uploaded_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
}

export interface AuthTokens {
  access_token: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface HealthCheck {
  status: string;
  postgres: boolean;
  redis: boolean;
  qdrant: boolean;
}
