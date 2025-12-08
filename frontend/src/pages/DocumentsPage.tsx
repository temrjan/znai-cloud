/**
 * Documents page - GitHub Copilot style
 */
import { useState, useEffect } from 'react';
import { Box } from '../components/common/Box';
import { useTheme } from '../contexts/ThemeContext';
import { useIsMobile, useIsDesktop } from '../hooks/useMediaQuery';
import { colors } from '../styles/theme';
import { documentsApi, quotaApi } from '../services/api';
import { Document, UserQuota, DocumentStatus } from '../types';
import {
  UploadIcon,
  TrashIcon,
  FileIcon,
  CheckIcon,
  XIcon,
  SyncIcon,
} from '@primer/octicons-react';

// Layout components
import { TopBar } from '../components/layout/TopBar';
import { MobileSidebar } from '../components/layout/MobileSidebar';
import { Sidebar } from '../components/layout/Sidebar';

export function DocumentsPage() {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const isMobile = useIsMobile();
  const isDesktop = useIsDesktop();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [quota, setQuota] = useState<UserQuota | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const visibility = 'organization' as const;

  useEffect(() => {
    loadData();
  }, []);

  // Auto-clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const loadData = async () => {
    try {
      const [docs, quotaData] = await Promise.all([
        documentsApi.list(),
        quotaApi.get(),
      ]);
      setDocuments(docs);
      setQuota(quotaData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents');
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
    setError('');

    try {
      await documentsApi.upload(file, visibility);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string, filename: string) => {
    if (!confirm(`Delete "${filename}"?`)) return;

    try {
      await documentsApi.delete(id);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        backgroundColor: themeColors.bg.primary,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Mobile: TopBar */}
      {isMobile && (
        <TopBar
          onMenuClick={() => setMobileMenuOpen(true)}
          title="Documents"
        />
      )}

      {/* Mobile: Sidebar overlay */}
      {isMobile && (
        <MobileSidebar
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Desktop: Fixed Sidebar */}
      {isDesktop && <Sidebar />}

      {/* Main content area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          marginLeft: isDesktop ? '240px' : 0,
          height: isMobile ? 'calc(100vh - 56px)' : '100vh',
          overflowY: 'auto',
        }}
      >
        <Box
          sx={{
            maxWidth: '900px',
            width: '100%',
            margin: '0 auto',
            padding: isMobile ? '16px' : '32px 24px',
          }}
        >
          {/* Header */}
          <Box sx={{ marginBottom: '24px' }}>
            <Box
              sx={{
                fontSize: isMobile ? '24px' : '28px',
                fontWeight: 600,
                color: themeColors.text.primary,
                marginBottom: '8px',
              }}
            >
              Documents
            </Box>
            {quota && (
              <Box
                sx={{
                  fontSize: '14px',
                  color: themeColors.text.secondary,
                }}
              >
                {quota.current_documents} of {quota.max_documents} documents used
              </Box>
            )}
          </Box>

          {/* Error message */}
          {error && (
            <Box
              sx={{
                padding: '12px 16px',
                backgroundColor: themeColors.accent.red,
                color: '#ffffff',
                borderRadius: '6px',
                fontSize: '14px',
                marginBottom: '16px',
              }}
            >
              {error}
            </Box>
          )}

          {/* Upload section */}
          <Box
            sx={{
              padding: '16px',
              backgroundColor: themeColors.bg.secondary,
              border: `1px solid ${themeColors.border.primary}`,
              borderRadius: '8px',
              marginBottom: '24px',
            }}
          >
            <input
              type="file"
              id="file-upload"
              onChange={handleFileUpload}
              disabled={uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5)}
              accept=".pdf,.txt,.md"
              style={{ display: 'none' }}
            />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <Box
                as="label"
                htmlFor="file-upload"
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  background: uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5)
                    ? themeColors.bg.tertiary
                    : themeColors.accent.blueGradient,
                  color: '#ffffff',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: 500,
                  cursor: uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5)
                    ? 'not-allowed'
                    : 'pointer',
                  opacity: uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5) ? 0.6 : 1,
                  '&:hover': uploading || (quota?.current_documents ?? 0) >= (quota?.max_documents ?? 5)
                    ? {}
                    : { opacity: 0.9 },
                }}
              >
                <UploadIcon size={16} />
                {uploading ? 'Uploading...' : 'Upload Document'}
              </Box>

              <Box sx={{ fontSize: '12px', color: themeColors.text.secondary }}>
                Документы доступны всей организации. Форматы: PDF, TXT, MD
              </Box>
            </Box>
          </Box>

          {/* Documents list */}
          {loading ? (
            <Box
              sx={{
                textAlign: 'center',
                padding: '48px',
                color: themeColors.text.secondary,
                fontSize: '14px',
              }}
            >
              Loading documents...
            </Box>
          ) : documents.length === 0 ? (
            <Box
              sx={{
                padding: '48px',
                textAlign: 'center',
                backgroundColor: themeColors.bg.secondary,
                border: `1px solid ${themeColors.border.primary}`,
                borderRadius: '8px',
              }}
            >
              <Box sx={{ marginBottom: '16px', color: themeColors.text.secondary }}>
                <FileIcon size={48} />
              </Box>
              <Box
                sx={{
                  fontSize: '18px',
                  fontWeight: 500,
                  color: themeColors.text.primary,
                  marginBottom: '8px',
                }}
              >
                No documents yet
              </Box>
              <Box sx={{ fontSize: '14px', color: themeColors.text.secondary }}>
                Upload your first document to get started
              </Box>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {documents.map((doc) => (
                <DocumentCard
                  key={doc.id}
                  document={doc}
                  onDelete={handleDelete}
                  themeColors={themeColors}
                />
              ))}
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}

// Document card component
interface DocumentCardProps {
  document: Document;
  onDelete: (id: string, filename: string) => void;
  themeColors: (typeof colors)['dark'] | (typeof colors)['light'];
}

function DocumentCard({ document: doc, onDelete, themeColors }: DocumentCardProps) {
  const getStatusDisplay = () => {
    switch (doc.status) {
      case DocumentStatus.PROCESSING:
        return {
          icon: <FileIcon size={16} />,
          text: 'Ready to index',
          color: themeColors.text.secondary,
        };
      case DocumentStatus.INDEXING:
        return {
          icon: <SyncIcon size={16} />,
          text: 'Indexing...',
          color: themeColors.accent.orange,
        };
      case DocumentStatus.INDEXED:
        return {
          icon: <CheckIcon size={16} />,
          text: 'Indexed',
          color: themeColors.accent.green,
        };
      case DocumentStatus.FAILED:
        return {
          icon: <XIcon size={16} />,
          text: 'Failed',
          color: themeColors.accent.red,
        };
    }
  };

  const status = getStatusDisplay();

  return (
    <Box
      sx={{
        padding: '16px',
        backgroundColor: themeColors.bg.secondary,
        border: `1px solid ${themeColors.border.primary}`,
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
      }}
    >
      {/* Left: File info */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <FileIcon size={16} />
          <Box
            sx={{
              fontSize: '14px',
              fontWeight: 500,
              color: themeColors.text.primary,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {doc.filename}
          </Box>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px' }}>
          <Box sx={{ color: themeColors.text.tertiary }}>
            {(doc.file_size / 1024).toFixed(1)} KB
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: '4px', color: status.color }}>
            {status.icon}
            {status.text}
          </Box>
          <Box sx={{ color: themeColors.text.tertiary }}>
            {new Date(doc.uploaded_at).toLocaleDateString()}
          </Box>
        </Box>
        {doc.error_message && (
          <Box
            sx={{
              marginTop: '4px',
              fontSize: '12px',
              color: themeColors.accent.red,
            }}
          >
            Error: {doc.error_message}
          </Box>
        )}
      </Box>

      {/* Right: Actions */}
      <Box sx={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
        {/* Delete button */}
        <Box
          as="button"
          onClick={() => onDelete(doc.id, doc.filename)}
          sx={{
            padding: '6px',
            backgroundColor: 'transparent',
            color: themeColors.text.secondary,
            border: `1px solid ${themeColors.border.primary}`,
            borderRadius: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            '&:hover': {
              backgroundColor: themeColors.accent.red,
              borderColor: themeColors.accent.red,
              color: '#ffffff',
            },
          }}
          aria-label="Delete document"
        >
          <TrashIcon size={14} />
        </Box>
      </Box>
    </Box>
  );
}
