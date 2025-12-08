/**
 * Chat page for RAG queries - with session support
 */
import { useState, useEffect, useRef } from 'react';
import { Box } from '../components/common/Box';
import { useTheme } from '../contexts/ThemeContext';
import { useIsMobile, useIsDesktop } from '../hooks/useMediaQuery';
import { colors } from '../styles/theme';
import { chatApi, chatSessionsApi, authApi } from '../services/api';
import type { ChatMessage as ChatMessageType } from '../types';

// Layout components
import { TopBar } from '../components/layout/TopBar';
import { MobileSidebar } from '../components/layout/MobileSidebar';
import { Sidebar } from '../components/layout/Sidebar';

// Chat components
import { ChatMessage, LoadingMessage } from '../components/chat/ChatMessage';
import { ChatInput } from '../components/chat/ChatInput';
import { MessageActions } from '../components/chat/MessageActions';

export function ChatPage() {
  const { theme } = useTheme();
  const themeColors = colors[theme];
  const isMobile = useIsMobile();
  const isDesktop = useIsDesktop();

  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const searchScope = 'all' as const;
  const [activeSessionId, setActiveSessionId] = useState<number | undefined>(undefined);
  const [sidebarRefresh, setSidebarRefresh] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const user = authApi.getCurrentUser();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load session messages when session changes
  const loadSessionMessages = async (sessionId: number) => {
    try {
      const session = await chatSessionsApi.get(sessionId);
      const loadedMessages: ChatMessageType[] = session.messages.map(msg => ({
        id: msg.id.toString(),
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.created_at),
        sources: msg.sources,
      }));
      setMessages(loadedMessages);
      setActiveSessionId(sessionId);
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  const handleSessionSelect = (sessionId: number) => {
    loadSessionMessages(sessionId);
  };

  const handleNewChat = () => {
    setMessages([]);
    setActiveSessionId(undefined);
  };

  const handleSend = async (input: string) => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatApi.query(input, searchScope, activeSessionId);

      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update active session and refresh sidebar
      if (response.session_id) {
        setActiveSessionId(response.session_id);
        setSidebarRefresh(prev => prev + 1);
      }
    } catch (err: any) {
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Ошибка: ${err.response?.data?.detail || 'Не удалось получить ответ. Попробуйте снова.'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
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
          title="Znai.cloud"
        />
      )}

      {/* Mobile: Sidebar overlay with chat history */}
      {isMobile && (
        <MobileSidebar
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
          activeSessionId={activeSessionId}
          onSessionSelect={handleSessionSelect}
          onNewChat={handleNewChat}
          refreshTrigger={sidebarRefresh}
        />
      )}

      {/* Desktop: Fixed Sidebar with session support */}
      {isDesktop && (
        <Sidebar
          activeSessionId={activeSessionId}
          onSessionSelect={handleSessionSelect}
          onNewChat={handleNewChat}
          refreshTrigger={sidebarRefresh}
        />
      )}

      {/* Main chat area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          marginLeft: isDesktop ? '240px' : 0,
          height: isMobile ? 'calc(100vh - 56px)' : '100vh',
          position: 'relative',
        }}
      >
        {/* Messages area */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            padding: isMobile ? '16px' : '24px 32px',
            paddingBottom: '24px',
          }}
        >
          {messages.length === 0 ? (
            // Empty state
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
              }}
            >
              <Box
                sx={{
                  fontSize: isMobile ? '20px' : '28px',
                  fontWeight: 600,
                  color: themeColors.text.primary,
                  marginBottom: '8px',
                }}
              >
                {getGreeting()}, {user?.full_name?.split(' ')[0] || 'User'}!
              </Box>
              <Box
                sx={{
                  fontSize: isMobile ? '14px' : '16px',
                  color: themeColors.text.secondary,
                }}
              >
                Задайте вопрос по вашим документам
              </Box>
            </Box>
          ) : (
            // Messages
            <Box
              sx={{
                maxWidth: '900px',
                margin: '0 auto',
                width: '100%',
              }}
            >
              {messages.map((message) => (
                <Box key={message.id}>
                  <ChatMessage message={message} />

                  {/* Actions for assistant messages */}
                  {message.role === 'assistant' && (
                    <MessageActions
                      onCopy={() => handleCopy(message.content)}
                      onLike={() => console.log('Like')}
                      onDislike={() => console.log('Dislike')}
                      onRefresh={() => console.log('Refresh')}
                    />
                  )}
                </Box>
              ))}

              {/* Loading indicator */}
              {loading && <LoadingMessage />}

              <div ref={messagesEndRef} />
            </Box>
          )}
        </Box>

        {/* Input area */}
        <Box
          sx={{
            padding: isMobile ? '16px' : '24px 0',
            paddingBottom: isMobile ? 'calc(16px + env(safe-area-inset-bottom))' : '32px',
          }}
        >

          <ChatInput
            onSend={handleSend}
            loading={loading}
            placeholder="Задайте вопрос..."
          />
        </Box>
      </Box>

    </Box>
  );
}

// Helper function
function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Доброе утро';
  if (hour < 18) return 'Добрый день';
  return 'Добрый вечер';
}
