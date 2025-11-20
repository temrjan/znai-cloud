/**
 * Admin page for user approval
 */
import { useState, useEffect } from "react";
import { Button, Flash, Text } from "@primer/react";
import { CheckIcon, XIcon, PersonIcon } from "@primer/octicons-react";
import { AppLayout } from "../components/layout/AppLayout";
import { adminApi } from "../services/api";
import { User } from "../types";

export function AdminPage() {
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    loadPendingUsers();
  }, []);

  const loadPendingUsers = async () => {
    try {
      const users = await adminApi.getPendingUsers();
      setPendingUsers(users);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load pending users");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId: string, email: string) => {
    try {
      await adminApi.approveUser(userId);
      setSuccess(`User ${email} approved successfully`);
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to approve user");
    }
  };

  const handleReject = async (userId: string, email: string) => {
    if (!confirm(`Reject user ${email}?`)) return;

    try {
      await adminApi.rejectUser(userId);
      setSuccess(`User ${email} rejected`);
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to reject user");
    }
  };

  return (
    <AppLayout>
      <div
        style={{
          maxWidth: "900px",
          margin: "0 auto",
          padding: "1.5rem",
        }}
      >
        <div style={{ marginBottom: "1.5rem" }}>
          <h1 style={{ fontSize: "1.5rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            User Management
          </h1>
          <Text as="p" style={{ color: "#57606a", fontSize: "0.875rem" }}>
            Approve or reject pending user registrations
          </Text>
        </div>

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

        {loading ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "#8b949e" }}>
            Loading pending users...
          </div>
        ) : pendingUsers.length === 0 ? (
          <div
            style={{
              backgroundColor: "white",
              borderRadius: "6px",
              border: "1px solid #d0d7de",
              padding: "3rem",
              textAlign: "center",
              color: "#8b949e",
            }}
          >
            <div style={{ marginBottom: "1rem" }}>
              <PersonIcon size={48} />
            </div>
            <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
              No pending approvals
            </p>
            <p style={{ fontSize: "0.875rem" }}>
              All user registrations have been processed
            </p>
          </div>
        ) : (
          <div
            style={{
              backgroundColor: "white",
              borderRadius: "6px",
              border: "1px solid #d0d7de",
              overflow: "hidden",
            }}
          >
            {pendingUsers.map((user) => (
              <div
                key={user.id}
                style={{
                  padding: "1.5rem",
                  borderBottom: "1px solid #d0d7de",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "1rem",
                  flexWrap: "wrap",
                }}
              >
                <div style={{ flex: 1, minWidth: "200px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
                    <PersonIcon size={16} />
                    <Text as="span" style={{ fontWeight: "600" }}>
                      {user.full_name}
                    </Text>
                  </div>
                  <Text as="p" style={{ fontSize: "0.875rem", color: "#57606a", marginBottom: "0.25rem" }}>
                    {user.email}
                  </Text>
                  <Text as="p" style={{ fontSize: "0.75rem", color: "#8b949e" }}>
                    Registered: {new Date(user.created_at).toLocaleString()}
                  </Text>
                </div>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <Button
                    variant="primary"
                    leadingVisual={CheckIcon}
                    onClick={() => handleApprove(user.id, user.email)}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="danger"
                    leadingVisual={XIcon}
                    onClick={() => handleReject(user.id, user.email)}
                  >
                    Reject
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
