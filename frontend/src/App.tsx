/**
 * Main application component with routing
 */
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import { ThemeProvider as PrimerThemeProvider, BaseStyles } from "@primer/react";
import { ThemeProvider } from "./contexts/ThemeContext";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ChatPage } from "./pages/ChatPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { AdminPage } from "./pages/AdminPage";
import { OrganizationSettingsPage } from "./pages/OrganizationSettingsPage";
import { authApi } from "./services/api";
import { UserRole } from "./types";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!authApi.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const user = authApi.getCurrentUser();

  if (!authApi.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== UserRole.ADMIN) {
    return <Navigate to="/chat" replace />;
  }

  return <>{children}</>;
}

function JoinRedirect() {
  const { code } = useParams<{ code: string }>();
  return <Navigate to={`/register?invite=${code}`} replace />;
}

export function App() {
  return (
    <ThemeProvider>
      <PrimerThemeProvider colorMode="auto">
        <BaseStyles>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/join/:code" element={<JoinRedirect />} />
              <Route
                path="/chat"
                element={
                  <ProtectedRoute>
                    <ChatPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/documents"
                element={
                  <ProtectedRoute>
                    <DocumentsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin"
                element={
                  <AdminRoute>
                    <AdminPage />
                  </AdminRoute>
                }
              />
              <Route
                path="/organization"
                element={
                  <ProtectedRoute>
                    <OrganizationSettingsPage />
                  </ProtectedRoute>
                }
              />
              <Route path="/" element={<Navigate to="/chat" replace />} />
            </Routes>
          </BrowserRouter>
        </BaseStyles>
      </PrimerThemeProvider>
    </ThemeProvider>
  );
}
