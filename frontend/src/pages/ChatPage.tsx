/**
 * Chat page for RAG queries
 */
import { useState, useEffect, useRef } from "react";
import { TextInput, Button, Flash, Text } from "@primer/react";
import { PaperAirplaneIcon } from "@primer/octicons-react";
import { AppLayout } from "../components/layout/AppLayout";
import { chatApi } from "../services/api";
import { ChatMessage } from "../types";

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await chatApi.query(input);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || "Failed to get response. Please try again.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div
        style={{
          height: "calc(100vh - 64px)",
          display: "flex",
          flexDirection: "column",
          maxWidth: "900px",
          margin: "0 auto",
          padding: "1rem",
        }}
      >
        <div style={{ marginBottom: "1rem" }}>
          <h1 style={{ fontSize: "1.5rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            Chat with your knowledge base
          </h1>
          <Text as="p" style={{ color: "#57606a", fontSize: "0.875rem" }}>
            Ask questions about your uploaded documents
          </Text>
        </div>

        {error && (
          <Flash variant="danger" style={{ marginBottom: "1rem" }}>
            {error}
          </Flash>
        )}

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            backgroundColor: "white",
            borderRadius: "6px",
            border: "1px solid #d0d7de",
            padding: "1rem",
            marginBottom: "1rem",
          }}
        >
          {messages.length === 0 ? (
            <div
              style={{
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#8b949e",
                textAlign: "center",
              }}
            >
              <div>
                <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
                  Start a conversation
                </p>
                <p style={{ fontSize: "0.875rem" }}>
                  Upload documents first, then ask questions about them
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  style={{
                    marginBottom: "1rem",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: message.role === "user" ? "flex-end" : "flex-start",
                  }}
                >
                  <div
                    style={{
                      maxWidth: "80%",
                      padding: "0.75rem 1rem",
                      borderRadius: "6px",
                      backgroundColor: message.role === "user" ? "#0969da" : "#f6f8fa",
                      color: message.role === "user" ? "white" : "#24292f",
                    }}
                  >
                    <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{message.content}</p>
                    {message.sources && message.sources.length > 0 && (
                      <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", opacity: 0.8 }}>
                        Sources: {message.sources.join(", ")}
                      </div>
                    )}
                  </div>
                  <span
                    style={{
                      fontSize: "0.75rem",
                      color: "#8b949e",
                      marginTop: "0.25rem",
                    }}
                  >
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem" }}>
          <TextInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            size="large"
            disabled={loading}
            style={{ flex: 1 }}
          />
          <Button
            type="submit"
            variant="primary"
            size="large"
            disabled={loading || !input.trim()}
            leadingVisual={PaperAirplaneIcon}
          >
            {loading ? "Sending..." : "Send"}
          </Button>
        </form>
      </div>
    </AppLayout>
  );
}
