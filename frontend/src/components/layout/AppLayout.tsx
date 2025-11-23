/**
 * Main application layout with navigation
 */
import { ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Header, Avatar } from "@primer/react";
import {
  SignOutIcon,
  CommentDiscussionIcon,
  FileIcon,
  ShieldLockIcon,
} from "@primer/octicons-react";
import { authApi } from "../../services/api";
import { UserRole } from "../../types";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = authApi.getCurrentUser();

  const handleLogout = () => {
    authApi.logout();
    navigate("/login");
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Header style={{ backgroundColor: "#24292f", padding: "1rem" }}>
        <Header.Item>
          <Header.Link
            onClick={() => navigate("/chat")}
            style={{
              color: "white",
              fontWeight: "bold",
              fontSize: "1.1rem",
              cursor: "pointer",
            }}
          >
            Znai.cloud
          </Header.Link>
        </Header.Item>

        <Header.Item full style={{ display: "flex", gap: "0.5rem" }}>
          <Header.Link
            onClick={() => navigate("/chat")}
            style={{
              color: isActive("/chat") ? "white" : "#8b949e",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <CommentDiscussionIcon size={16} />
            <span style={{ display: window.innerWidth > 768 ? "inline" : "none" }}>
              Chat
            </span>
          </Header.Link>

          <Header.Link
            onClick={() => navigate("/documents")}
            style={{
              color: isActive("/documents") ? "white" : "#8b949e",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <FileIcon size={16} />
            <span style={{ display: window.innerWidth > 768 ? "inline" : "none" }}>
              Documents
            </span>
          </Header.Link>

          {user?.role === UserRole.ADMIN && (
            <Header.Link
              onClick={() => navigate("/admin")}
              style={{
                color: isActive("/admin") ? "white" : "#8b949e",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
              }}
            >
              <ShieldLockIcon size={16} />
              <span style={{ display: window.innerWidth > 768 ? "inline" : "none" }}>
                Admin
              </span>
            </Header.Link>
          )}
        </Header.Item>

        <Header.Item style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <span style={{ color: "#8b949e", fontSize: "0.875rem" }}>
            {user?.email}
          </span>
          <Avatar
            src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name || "User")}&background=0969da&color=fff`}
            size={32}
          />
          <Header.Link
            onClick={handleLogout}
            style={{
              color: "#8b949e",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
            }}
          >
            <SignOutIcon size={16} />
          </Header.Link>
        </Header.Item>
      </Header>

      <main style={{ flex: 1, backgroundColor: "#f6f8fa" }}>
        {children}
      </main>
    </div>
  );
}
