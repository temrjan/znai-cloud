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
  organization_name?: string;
  invite_code?: string;
}

export interface HealthCheck {
  status: string;
  postgres: boolean;
  redis: boolean;
  qdrant: boolean;
}

// Organization types
export interface Organization {
  id: number;
  name: string;
  slug: string;
  owner_id: number;
  max_members: number;
  max_documents: number;
  status: string;
  created_at: string;
}

export interface OrganizationMember {
  id: number;
  user_id: number;
  email: string;
  full_name: string;
  role: string;
  joined_at: string;
}

export interface OrganizationInvite {
  id: number;
  code: string;
  max_uses: number;
  used_count: number;
  default_role: string;
  expires_at: string;
  status: string;
  created_at: string;
}

export interface OrganizationSettings {
  id: number;
  organization_id: number;
  custom_system_prompt?: string;
  custom_temperature?: number;
  custom_max_tokens?: number;
  custom_terminology?: Record<string, string>;
  chunk_size?: number;
  chunk_overlap?: number;
  search_top_k?: number;
  response_language?: string;
  enable_citations?: boolean;
}

export interface OrganizationStats {
  total_members: number;
  total_documents: number;
  total_queries_today: number;
  storage_used_mb: number;
}

// Admin types
export interface PendingOrganization {
  id: number;
  name: string;
  slug: string;
  status: string;
  created_at: string;
  owner_id: number;
  owner_email: string;
  owner_full_name: string;
}

export interface AdminStats {
  pending_users: number;
  pending_organizations: number;
  total_pending: number;
}

// Public invite details (for registration page)
export interface InviteDetails {
  code: string;
  organization_name: string;
  expires_at: string;
  is_valid: boolean;
  remaining_uses: number;
}
