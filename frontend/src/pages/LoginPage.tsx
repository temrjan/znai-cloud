/**
 * Login page with mobile-first design
 */
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button, FormControl, TextInput, Flash, Heading, Text } from "@primer/react";
import { authApi } from "../services/api";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authApi.login({ email, password });
      navigate("/chat");
    } catch (err: any) {
      const message = err.response?.data?.detail || "Login failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

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
          maxWidth: "400px",
          backgroundColor: "white",
          borderRadius: "6px",
          border: "1px solid #d0d7de",
          padding: "2rem",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <Heading as="h1" style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>
            Znai.cloud
          </Heading>
          <Text as="p" style={{ color: "#57606a" }}>
            Sign in to your knowledge base
          </Text>
        </div>

        {error && (
          <Flash variant="danger" style={{ marginBottom: "1rem" }}>
            {error}
          </Flash>
        )}

        <FormControl required style={{ marginBottom: "1rem" }}>
          <FormControl.Label>Email</FormControl.Label>
          <TextInput
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            size="large"
            block
            disabled={loading}
          />
        </FormControl>

        <FormControl required style={{ marginBottom: "1.5rem" }}>
          <FormControl.Label>Password</FormControl.Label>
          <TextInput
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
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
          {loading ? "Signing in..." : "Sign in"}
        </Button>

        <Text as="p" style={{ textAlign: "center", fontSize: "0.875rem", color: "#57606a" }}>
          Don't have an account?{" "}
          <Link to="/register" style={{ color: "#0969da" }}>
            Register
          </Link>
        </Text>
      </form>
    </div>
  );
}
