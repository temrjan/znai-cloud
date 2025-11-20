/**
 * Main application component with routing
 */
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, BaseStyles } from "@primer/react";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ChatPage } from "./pages/ChatPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { AdminPage } from "./pages/AdminPage";
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

export function App() {
  return (
    <ThemeProvider colorMode="auto">
      <BaseStyles>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
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
            <Route path="/" element={<Navigate to="/chat" replace />} />
          </Routes>
        </BrowserRouter>
      </BaseStyles>
    </ThemeProvider>
  );
}
