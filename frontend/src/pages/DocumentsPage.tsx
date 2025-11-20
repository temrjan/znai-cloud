/**
 * Documents management page
 */
import { useState, useEffect } from "react";
import { Button, Flash, Text, IconButton } from "@primer/react";
import { UploadIcon, TrashIcon, FileIcon } from "@primer/octicons-react";
import { AppLayout } from "../components/layout/AppLayout";
import { documentsApi, quotaApi } from "../services/api";
import { Document, UserQuota, DocumentStatus } from "../types";

export function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [quota, setQuota] = useState<UserQuota | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  // Auto-clear error and success messages after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const loadData = async () => {
    try {
      const [docs, quotaData] = await Promise.all([
        documentsApi.list(),
        quotaApi.get(),
      ]);
      setDocuments(docs);
      setQuota(quotaData);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (quota && quota.current_documents >= quota.max_documents) {
      setError(`You've reached your limit of ${quota.max_documents} documents`);
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      await documentsApi.upload(file);
      setSuccess(`"${file.name}" uploaded successfully`);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload document");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (id: string, filename: string) => {
    if (!confirm(`Delete "${filename}"?`)) return;

    try {
      await documentsApi.delete(id);
      setSuccess(`"${filename}" deleted successfully`);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete document");
    }
  };

  const handleIndex = async (id: string, filename: string) => {
    try {
      setSuccess(`Indexing "${filename}"...`);
      await documentsApi.index(id);
      setSuccess(`"${filename}" indexed successfully`);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to index document");
    }
  };

  const getStatusColor = (status: DocumentStatus) => {
    switch (status) {
      case DocumentStatus.INDEXED:
        return "#1a7f37";
      case DocumentStatus.PROCESSING:
        return "#bf8700";
      case DocumentStatus.FAILED:
        return "#cf222e";
      default:
        return "#8b949e";
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
            Documents
          </h1>
          {quota && (
            <Text as="p" style={{ color: "#57606a", fontSize: "0.875rem" }}>
              {quota.current_documents} of {quota.max_documents} documents used
            </Text>
          )}
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

        <div
          style={{
            backgroundColor: "white",
            borderRadius: "6px",
            border: "1px solid #d0d7de",
            padding: "1.5rem",
            marginBottom: "1.5rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <input
              type="file"
              id="file-upload"
              onChange={handleFileUpload}
              disabled={uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5)}
              accept=".pdf,.doc,.docx,.txt,.md"
              style={{ display: "none" }}
            />
            <Button
              as="label"
              htmlFor="file-upload"
              variant="primary"
              leadingVisual={UploadIcon}
              disabled={uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5)}
            >
              {uploading ? "Uploading..." : "Upload Document"}
            </Button>
            <Text as="span" style={{ color: "#57606a", fontSize: "0.875rem" }}>
              Supported: PDF, DOC, DOCX, TXT, MD
            </Text>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "#8b949e" }}>
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
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
              <FileIcon size={48} />
            </div>
            <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
              No documents yet
            </p>
            <p style={{ fontSize: "0.875rem" }}>
              Upload your first document to get started
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
            {documents.map((doc) => (
              <div
                key={doc.id}
                style={{
                  padding: "1rem",
                  borderBottom: "1px solid #d0d7de",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "1rem",
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <FileIcon size={16} />
                    <Text
                      as="span"
                      style={{
                        fontWeight: "600",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {doc.filename}
                    </Text>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginTop: "0.25rem" }}>
                    <Text as="span" style={{ fontSize: "0.75rem", color: "#57606a" }}>
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </Text>
                    <Text
                      as="span"
                      style={{
                        fontSize: "0.75rem",
                        color: getStatusColor(doc.status),
                        fontWeight: "500",
                      }}
                    >
                      {doc.status}
                    </Text>
                    <Text as="span" style={{ fontSize: "0.75rem", color: "#8b949e" }}>
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </Text>
                  </div>
                  {doc.error_message && (
                    <Text as="p" style={{ fontSize: "0.75rem", color: "#cf222e", marginTop: "0.25rem" }}>
                      Error: {doc.error_message}
                    </Text>
                  )}
                </div>
                <div style={{ display: "flex", gap: "8px" }}>
                  {doc.status === DocumentStatus.PROCESSING && (
                    <Button
                      size="small"
                      onClick={() => handleIndex(doc.id, doc.filename)}
                    >
                      Index
                    </Button>
                  )}
                  <IconButton
                    aria-label="Delete document"
                    icon={TrashIcon}
                    variant="danger"
                    onClick={() => handleDelete(doc.id, doc.filename)}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
