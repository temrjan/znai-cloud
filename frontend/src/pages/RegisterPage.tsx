/**
 * Registration page with mobile-first design
 */
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button, FormControl, TextInput, Flash, Heading, Text } from "@primer/react";
import { authApi } from "../services/api";

export function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      await authApi.register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });
      setSuccess(true);
    } catch (err: any) {
      const message = err.response?.data?.detail || "Registration failed. Please try again.";
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
            Registration successful!
          </Flash>
          <Heading as="h2" style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>
            Awaiting Approval
          </Heading>
          <Text as="p" style={{ color: "#57606a", marginBottom: "1.5rem" }}>
            Your account has been created and is pending admin approval. You will be able to log
            in once approved.
          </Text>
          <Button onClick={() => navigate("/login")} variant="primary" size="large">
            Go to Login
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
          maxWidth: "400px",
          backgroundColor: "white",
          borderRadius: "6px",
          border: "1px solid #d0d7de",
          padding: "2rem",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <Heading as="h1" style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>
            Create Account
          </Heading>
          <Text as="p" style={{ color: "#57606a" }}>
            Join AI-Avangard knowledge platform
          </Text>
        </div>

        {error && (
          <Flash variant="danger" style={{ marginBottom: "1rem" }}>
            {error}
          </Flash>
        )}

        <FormControl required style={{ marginBottom: "1rem" }}>
          <FormControl.Label>Full Name</FormControl.Label>
          <TextInput
            value={formData.full_name}
            onChange={(e) => handleChange("full_name", e.target.value)}
            placeholder="John Doe"
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

        <FormControl required style={{ marginBottom: "1rem" }}>
          <FormControl.Label>Password</FormControl.Label>
          <TextInput
            type="password"
            value={formData.password}
            onChange={(e) => handleChange("password", e.target.value)}
            placeholder="At least 8 characters"
            size="large"
            block
            disabled={loading}
          />
        </FormControl>

        <FormControl required style={{ marginBottom: "1.5rem" }}>
          <FormControl.Label>Confirm Password</FormControl.Label>
          <TextInput
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => handleChange("confirmPassword", e.target.value)}
            placeholder="Repeat password"
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
          {loading ? "Creating account..." : "Create account"}
        </Button>

        <Text as="p" style={{ textAlign: "center", fontSize: "0.875rem", color: "#57606a" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "#0969da" }}>
            Sign in
          </Link>
        </Text>
      </form>
    </div>
  );
}
